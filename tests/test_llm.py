from pathlib import Path

from talkbot import llm as llm_module
from talkbot.tools import register_all_tools, reset_runtime_state


def test_local_provider_uses_repo_default_model_path(monkeypatch, tmp_path):
    model_dir = tmp_path / "models"
    model_dir.mkdir(parents=True)
    model_path = model_dir / "default.gguf"
    model_path.write_bytes(b"gguf")

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TALKBOT_LOCAL_MODEL_PATH", raising=False)
    monkeypatch.delenv("TALKBOT_LOCAL_N_CTX", raising=False)

    captured = {}

    class DummyLocalClient:
        def __init__(
            self,
            *,
            model_path,
            binary="llama-cli",
            n_ctx=2048,
            enable_thinking=False,
            temperature=0.7,
            max_tokens=512,
            direct_tool_routing=False,
        ):
            captured["model_path"] = model_path
            captured["binary"] = binary
            captured["n_ctx"] = n_ctx
            captured["enable_thinking"] = enable_thinking

    monkeypatch.setattr(llm_module, "LocalLlamaCppClient", DummyLocalClient)

    llm_module.create_llm_client(provider="local", model="qwen/qwen3-1.7b")

    assert Path(captured["model_path"]).resolve() == model_path.resolve()
    assert captured["binary"] == "llama-cli"
    assert captured["n_ctx"] == 2048
    assert captured["enable_thinking"] is False


def test_rewrite_recall_to_remember_for_explicit_remember_intent():
    name, args = llm_module._rewrite_tool_call_for_user_intent(
        "recall",
        {"key": "favorite_color"},
        "Remember that my favorite color is blue.",
    )
    assert name == "remember"
    assert args == {"key": "favorite_color", "value": "blue"}


def test_openrouter_provider_uses_env_api_key(monkeypatch):
    captured = {}

    class DummyOpenRouterClient:
        def __init__(self, *, api_key, model, site_url=None, site_name=None):
            captured["api_key"] = api_key
            captured["model"] = model
            captured["site_url"] = site_url
            captured["site_name"] = site_name

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(llm_module, "OpenRouterClient", DummyOpenRouterClient)

    client = llm_module.create_llm_client(
        provider="openrouter",
        model="ibm-granite/granite-4.0-h-micro",
    )

    assert captured["api_key"] == "test-key"
    assert captured["model"] == "ibm-granite/granite-4.0-h-micro"
    assert getattr(client, "provider_name", "") == "openrouter"


def test_normalize_add_to_list_item_list_alias():
    """Model passes item_list=[...] to add_to_list — should remap to items."""
    from talkbot.llm import _normalize_tool_args_for_call
    result = _normalize_tool_args_for_call(
        "add_to_list", {"item_list": ["milk"], "list_name": "grocery"}
    )
    assert result == {"items": ["milk"], "list_name": "grocery"}


def test_normalize_add_to_list_item_alias():
    """Model passes old singular 'item' param — should remap to items."""
    from talkbot.llm import _normalize_tool_args_for_call
    result = _normalize_tool_args_for_call(
        "add_to_list", {"item": "eggs", "list_name": "grocery"}
    )
    assert result == {"items": "eggs", "list_name": "grocery"}


def test_direct_tool_calls_parse_memory_phrasing():
    remember_calls = llm_module._direct_tool_calls_from_user(
        [{"role": "user", "content": "Remember that my project codename is Falcon."}]
    )
    recall_calls = llm_module._direct_tool_calls_from_user(
        [{"role": "user", "content": "What did you remember about my project codename?"}]
    )

    assert remember_calls == [
        {
            "id": "direct-remember-0",
            "function": {
                "name": "remember",
                "arguments": '{"key": "project_codename", "value": "falcon"}',
            },
        }
    ]
    assert recall_calls == [
        {
            "id": "direct-recall-0",
            "function": {
                "name": "recall",
                "arguments": '{"key": "project_codename"}',
            },
        }
    ]


def test_direct_tool_calls_do_not_misroute_math_question_to_recall():
    calc_calls = llm_module._direct_tool_calls_from_user(
        [{"role": "user", "content": "What is 15 percent of 47 dollars?"}]
    )

    assert calc_calls == [
        {
            "id": "direct-calc-percent-0",
            "function": {
                "name": "calculator",
                "arguments": '{"formula": "(15/100)*47"}',
            },
        }
    ]


def test_direct_tool_calls_parse_list_create_add_and_read():
    create_calls = llm_module._direct_tool_calls_from_user(
        [{"role": "user", "content": "Create a grocery list and add milk."}]
    )
    read_calls = llm_module._direct_tool_calls_from_user(
        [{"role": "user", "content": "What is on my grocery list?"}]
    )

    assert create_calls == [
        {
            "id": "direct-create-list-0",
            "function": {
                "name": "create_list",
                "arguments": '{"list_name": "grocery"}',
            },
        },
        {
            "id": "direct-add-list-0",
            "function": {
                "name": "add_to_list",
                "arguments": '{"list_name": "grocery", "items": "milk"}',
            },
        },
    ]
    assert read_calls == [
        {
            "id": "direct-get-list-0",
            "function": {
                "name": "get_list",
                "arguments": '{"list_name": "grocery"}',
            },
        }
    ]


def test_local_server_direct_routing_persists_memory_without_model(monkeypatch, tmp_path):
    monkeypatch.setenv("TALKBOT_DATA_DIR", str(tmp_path / "talkbot-data"))
    reset_runtime_state(clear_persistent=True)
    client = llm_module.LocalServerClient(
        model="qwen3.5-0.8b-q8_0.gguf",
        base_url="http://127.0.0.1:8000/v1",
        direct_tool_routing=True,
    )
    register_all_tools(client)
    monkeypatch.setattr(
        client,
        "chat_completion",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("model should not be called")),
    )

    stored = client.chat_with_tools(
        [{"role": "user", "content": "Remember that my project codename is Falcon."}]
    )
    recalled = client.chat_with_tools(
        [{"role": "user", "content": "What did you remember about my project codename?"}]
    )

    assert "Remembered: project_codename = falcon" == stored
    assert "project_codename: falcon" == recalled


def test_local_server_direct_routing_persists_list_without_model(monkeypatch, tmp_path):
    monkeypatch.setenv("TALKBOT_DATA_DIR", str(tmp_path / "talkbot-data"))
    reset_runtime_state(clear_persistent=True)
    client = llm_module.LocalServerClient(
        model="qwen3.5-0.8b-q8_0.gguf",
        base_url="http://127.0.0.1:8000/v1",
        direct_tool_routing=True,
    )
    register_all_tools(client)
    monkeypatch.setattr(
        client,
        "chat_completion",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("model should not be called")),
    )

    created = client.chat_with_tools(
        [{"role": "user", "content": "Create a grocery list and add milk."}]
    )
    listed = client.chat_with_tools(
        [{"role": "user", "content": "What is on my grocery list?"}]
    )

    assert created == "Created 'grocery' list.\nAdded 'milk' to the grocery list."
    assert listed == "Grocery list:\n- milk"
