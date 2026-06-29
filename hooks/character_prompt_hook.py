# hooks/character_prompt_hook.py
"""
Character Prompt Hooker (Improved with debugging)

메인 프롬프트에 :c1 "태그" :c2 "태그" 문법이 있으면
자동으로 CharacterModule에 주입하는 Hooker
"""

from core.character_tag_parser import has_character_tags, parse_character_tags, remove_character_tags
from core.character_prompt_injector import inject_character_tags_to_module


def process_character_tags_from_main_prompt(app_context, remove_from_prompt: bool = True) -> bool:
    """
    메인 프롬프트에서 :cN "태그" 문법을 감지하고
    CharacterModule에 주입합니다.
    """
    try:
        print("[CharacterPromptHook] === 함수 호출됨 ===")

        if not hasattr(app_context, 'main_window'):
            print("[CharacterPromptHook] main_window 없음")
            return False

        main_prompt_widget = getattr(app_context.main_window, 'main_prompt_textedit', None)
        if main_prompt_widget is None:
            print("[CharacterPromptHook] main_prompt_textedit 없음")
            return False

        main_prompt = main_prompt_widget.toPlainText()
        print("[CharacterPromptHook] 프롬프트 길이:", len(main_prompt))
        print("[CharacterPromptHook] 프롬프트 앞부분:", main_prompt[:200] if main_prompt else "(empty)")

        if not has_character_tags(main_prompt):
            print("[CharacterPromptHook] :cN 문법 없음 → 종료")
            return False

        print("[CharacterPromptHook] :cN 문법 발견!")

        tags = parse_character_tags(main_prompt)
        print("[CharacterPromptHook] 파싱 결과:", tags)

        if not tags:
            print("[CharacterPromptHook] 파싱 결과가 비어있음")
            return False

        success = inject_character_tags_to_module(app_context, tags, also_update_ui=True)
        print("[CharacterPromptHook] CharacterModule 주입 성공:", success)

        if success and remove_from_prompt:
            clean_prompt = remove_character_tags(main_prompt)
            main_prompt_widget.setPlainText(clean_prompt)
            print("[CharacterPromptHook] 메인 프롬프트에서 :cN 문법 제거 완료")

        return success

    except Exception as e:
        print(f"[CharacterPromptHook] 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
# ==================== 🆕 시퀀스 등 내부 사용을 위한 헬퍼 함수 ====================

def apply_character_tags_to_prompt(
    prompt: str, 
    app_context, 
    remove_from_prompt: bool = True,
    update_main_ui: bool = False
) -> str:
    """
    프롬프트 문자열을 받아 :cN 문법을 처리하고, 처리된 프롬프트를 반환합니다.
    
    일반 생성에서는 update_main_ui=True로 호출하면 기존과 동일하게 동작하고,
    시퀀스처럼 내부 처리만 하고 싶을 때는 update_main_ui=False로 호출하면
    메인 프롬프트 입력창은 건드리지 않습니다.
    
    Returns:
        처리 후 깨끗해진 프롬프트 문자열
    """
    if not has_character_tags(prompt):
        return prompt

    tags = parse_character_tags(prompt)
    if not tags:
        return prompt

    # CharacterModule에 태그 주입
    success = inject_character_tags_to_module(app_context, tags, also_update_ui=True)

    cleaned_prompt = prompt
    if success and remove_from_prompt:
        cleaned_prompt = remove_character_tags(prompt)

        # update_main_ui가 True일 때만 메인 프롬프트 입력창 수정
        if update_main_ui:
            try:
                main_prompt_widget = getattr(app_context.main_window, 'main_prompt_textedit', None)
                if main_prompt_widget:
                    main_prompt_widget.setPlainText(cleaned_prompt)
            except Exception as e:
                print(f"[CharacterPromptHook] 메인 UI 수정 중 오류: {e}")

    return cleaned_prompt