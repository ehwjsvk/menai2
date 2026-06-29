# core/character_tag_parser.py
"""
Character Tag Parser

메인 프롬프트에서 :c1 "태그들" :c2 "태그들" 형태를 파싱하는 클래스
"""

import re
from typing import Dict


class CharacterTagParser:
    """
    메인 프롬프트에서 :cN "태그" 문법을 파싱하는 클래스
    """

    # :c1, :c2, :C1 등 대소문자 무시하고 인식
    _PATTERN = re.compile(r':c(\d+)\s*"([^"]*)"', re.IGNORECASE)

    def parse(self, text: str) -> Dict[int, str]:
        """
        :c1 "태그" :c2 "태그" 형태를 파싱하여 반환
        Returns: {캐릭터 번호: 태그 문자열}
        """
        if not text or not isinstance(text, str):
            return {}

        result: Dict[int, str] = {}

        for match in self._PATTERN.finditer(text):
            char_index = int(match.group(1))
            tags = match.group(2).strip()

            if tags:  # 빈 문자열 제외
                result[char_index] = tags

        return result

    def has_character_tags(self, text: str) -> bool:
        """텍스트에 :cN "..." 같은 캐릭터 태그 문법이 있는지 확인"""
        if not text:
            return False
        return bool(self._PATTERN.search(text))

    def remove_character_tags(self, text: str) -> str:
        """메인 프롬프트에서 :cN "..." 부분만 제거한 문자열 반환"""
        if not text:
            return text
        return self._PATTERN.sub("", text).strip()


# ==================== 편의용 Top-level 함수들 ====================
def parse_character_tags(text: str) -> Dict[int, str]:
    """ :c1 "..." :c2 "..." 문법을 파싱하여 {1: tags, 2: tags} 반환 """
    return CharacterTagParser().parse(text)

def has_character_tags(text: str) -> bool:
    """ 텍스트에 :cN "..." 문법이 있는지 여부 """
    return CharacterTagParser().has_character_tags(text)

def remove_character_tags(text: str) -> str:
    """ :cN "..." 부분을 제거한 프롬프트 반환 """
    return CharacterTagParser().remove_character_tags(text)