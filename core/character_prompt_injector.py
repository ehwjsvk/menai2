# core/character_prompt_injector.py
"""
Character Prompt Injector

:c1 "태그" :c2 "태그" 문법을 파싱하여 CharacterModule의 modifiable_clone에 주입하는 로직

사용 예시 (Hooker에서):
    from core.character_prompt_injector import inject_character_tags_to_module
    from core.character_tag_parser import parse_character_tags

    # 메인 프롬프트에서 :cN 문법 파싱
    tags = parse_character_tags(main_prompt)

    # CharacterModule에 주입
    success = inject_character_tags_to_module(app_context, tags)
    if success:
        print("성공적으로 캐릭터 태그 주입")
"""

from typing import Dict, Optional


def inject_character_tags_to_module(
    app_context,
    character_tags: Dict[int, str],
    also_update_ui: bool = True
) -> bool:
    """
    :c1, :c2 문법으로 파싱된 태그를 CharacterModule에 주입합니다.

    Args:
        app_context: NAIA 앱 컨텍스트
        character_tags: {1: "long hair...", 2: "short hair..."} 형태의 디셔너리
        also_update_ui: True이면 hooker_update_prompt()를 호출해 UI도 갱신

    Returns:
        True: 성공
        False: CharacterModule을 찾지 못함 또는 주입 실패
    """
    if not character_tags:
        return False

    try:
        # CharacterModule 인스턴스 가져오기
        middle_section = getattr(app_context, 'middle_section_controller', None)
        if not middle_section:
            print("[CharacterPromptInjector] middle_section_controller 를 찾을 수 없습니다.")
            return False

        character_module = middle_section.get_module_instance("CharacterModule")
        if not character_module:
            print("[CharacterPromptInjector] CharacterModule을 찾을 수 없습니다.")
            return False

        # modifiable_clone 가져오기
        clone = character_module.get_character_modifiable_clone()
        if not isinstance(clone, dict):
            print("[CharacterPromptInjector] modifiable_clone을 가져올 수 없습니다.")
            return False

        # characters 리스트 확보
        if 'characters' not in clone:
            clone['characters'] = []
        if 'uc' not in clone:
            clone['uc'] = []

        # 태그 주입
        for char_index, tags in sorted(character_tags.items()):
            # 인덱스는 0-based
            list_index = char_index - 1

            # 리스트 길이 확보
            while len(clone['characters']) <= list_index:
                clone['characters'].append("")
            while len(clone['uc']) <= list_index:
                clone['uc'].append("")

            # 태그 설정
            clone['characters'][list_index] = tags
            # UC는 비워둡 (필요시 확장 가능)

            print(f"[CharacterPromptInjector] C{char_index} 에 태그 주입: {tags[:50]}...")

        # CharacterModule 활성화
        if hasattr(character_module, 'activate_checkbox'):
            if not character_module.activate_checkbox.isChecked():
                character_module.activate_checkbox.setChecked(True)
                print("[CharacterPromptInjector] CharacterModule 자동 활성화")

        # UI 갱신
        if also_update_ui and hasattr(character_module, 'hooker_update_prompt'):
            character_module.hooker_update_prompt()
            print("[CharacterPromptInjector] UI 갱신 완료")

        return True

    except Exception as e:
        print(f"[CharacterPromptInjector] 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return False
