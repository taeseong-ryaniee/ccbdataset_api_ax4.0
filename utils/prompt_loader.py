#!/usr/bin/env python3
"""
프롬프트 로더 유틸리티
- 외부 프롬프트 파일을 읽어서 템플릿 변수를 치환
"""

from pathlib import Path
from typing import Dict, Any


class PromptLoader:
    """프롬프트 템플릿 로더"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._cache = {}  # 프롬프트 캐싱
        
        # 공통 템플릿 정의 (수치 정보 추상화)
        self.artwork_info_template = """**작품 기본 정보:**
- 작품명: {artwork_title}
- 작가: {artist_name} ({nationality})
- 제작연도: {creation_year}
- 규모: {size_description}
- 소재: {materials}
- 기법: {technique}
- 장르: 현대공예

**작품 개념:**
{filtered_concept}"""

        self.artist_info_template = """**작가 정보:**
- 작가: {artist_name} ({nationality})
- 생년: {birth_year}
- 학력: {education}
- 주요 전시 경력: {major_exhibitions}
- 수상 경력: {awards}

**작가 활동:**
{artist_activities}"""

        self.json_output_format = """### 출력 형식
반드시 아래 JSON 형식으로 출력해주세요:

```json
[
  {{
    "instruction": "질문 내용 (반드시 작가명과 작품명 포함)",
    "input": "",
    "output": "답변 내용 (반드시 작가명과 작품명 포함, 구체적 수치 언급 금지)"
  }}
]
```

### 필수 요구사항: 작가명과 작품명 포함
- **모든 질문과 답변에 작가명과 작품명을 반드시 포함해야 합니다**
- 질문 예시: "{artist_name}의 '{artwork_title}'에서 어떤 감정을 느낄 수 있나요?"
- 답변 예시: "{artist_name}의 '{artwork_title}'는 관람객들에게..."
- 대명사("이 작품", "작가", "그것") 사용 절대 금지

### 중요: 답변 작성 원칙
1. **작가명과 작품명을 모든 Q&A에 필수 포함**
2. 구체적인 수치(크기, 무게, 정확한 규격) 언급 절대 금지
3. 일반적인 형식, 말투, 추론 방식에 집중
4. "소규모", "중간 규모", "대규모" 등 추상적 표현 사용
5. 예술적 해석과 감상에 중점"""
    
    def load_prompt(self, prompt_name: str) -> str:
        """프롬프트 파일 로드 (캐싱 지원)"""
        if prompt_name in self._cache:
            return self._cache[prompt_name]
        
        prompt_file = self.prompts_dir / f"{prompt_name}.md"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {prompt_file}")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._cache[prompt_name] = content
        return content
    
    def _filter_numerical_content(self, text: str) -> str:
        """텍스트에서 구체적인 수치 정보 제거"""
        if not text:
            return "작품의 깊이 있는 예술적 의도를 담고 있습니다."
            
        import re
        
        # 구체적인 수치 패턴 제거
        filtered_text = text
        
        # 치수 패턴 제거 (예: 100×4×100cm, 29.5×29.5×55cm)
        filtered_text = re.sub(r'\d+(?:\.\d+)?[×x]\d+(?:\.\d+)?[×x]\d+(?:\.\d+)?(?:cm|mm|m)?', '[적절한 크기]', filtered_text)
        
        # 단일 치수 패턴 제거 (예: 100cm, 29.5cm)
        filtered_text = re.sub(r'\d+(?:\.\d+)?(?:cm|mm|m)\b', '[적정 규모]', filtered_text)
        
        # 무게 패턴 제거 (예: 5kg, 2.5kg, 100g)
        filtered_text = re.sub(r'\d+(?:\.\d+)?\s*(?:kg|g)\b', '[적절한 무게]', filtered_text)
        
        # 연도 패턴은 보존 (예술적 맥락에서 중요)
        # 기타 구체적 수치는 제거하되 예술적 표현 유지
        
        return filtered_text.strip()

    def _filter_exhibition_awards_content(self, content) -> str:
        """전시/수상 이력에서 불필요한 수치 제거 (연도는 보존)"""
        if not content:
            return "다양한 활동"
            
        # 리스트인 경우
        if isinstance(content, list):
            if not content:
                return "다양한 활동"
            # 처음 3개 정도만 표시하고 수치 제거
            filtered_items = []
            for item in content[:3]:
                # 연도는 보존하되 구체적 수치는 제거
                filtered_item = str(item)
                # 상세한 수치나 주소 등은 간략화
                if len(filtered_item) > 100:
                    filtered_item = filtered_item[:100] + "..."
                filtered_items.append(filtered_item)
            return "; ".join(filtered_items)
        
        # 문자열인 경우
        content_str = str(content)
        if len(content_str) > 200:
            content_str = content_str[:200] + "..."
        return content_str

    def _format_artwork_info(self, artwork: Dict[str, Any]) -> str:
        """작품 정보 포맷팅 (수치 추상화)"""
        # 크기 정보를 추상화된 표현으로 변환 (여러 키 확인)
        size_raw = artwork.get("크기") or artwork.get("사이즈") or artwork.get("size", "")
        size_description = self._abstract_size_info(size_raw)
        
        # 재료 정보 (여러 키 확인)
        materials = artwork.get("재료") or artwork.get("소재") or artwork.get("소재 번역") or artwork.get("materials", "N/A")
        
        # 작품 개념 필터링 (작가 노트나 설명에서 수치 제거)
        artist_note = artwork.get("작가노트", "")
        description = artwork.get("작품설명", "")
        
        # 작가 노트와 설명 합치고 수치 필터링
        concept_text = f"{description}\n\n{artist_note}".strip()
        filtered_concept = self._filter_numerical_content(concept_text)
        
        return self.artwork_info_template.format(
            artwork_title=artwork.get("제목", artwork.get("작품명", "N/A")),
            artist_name=artwork.get("작가", artwork.get("성명", "N/A")),
            nationality=artwork.get("국적", "N/A"),
            creation_year=artwork.get("제작년도", artwork.get("제작연도", "N/A")),
            size_description=size_description,
            materials=materials,
            technique=artwork.get("기법", "현대공예"),
            filtered_concept=filtered_concept
        )
    
    def _abstract_size_info(self, size_str: str) -> str:
        """크기 정보를 추상적 표현으로 변환 (수치 완전 제거)"""
        if not size_str or size_str in ["", "N/A"]:
            return "적절한 규모"
            
        # 구체적인 수치 완전 제거하고 추상적 표현으로 변환
        size_lower = str(size_str).lower()
        
        # 수치 패턴 감지 (cm, mm, m, kg 등)
        import re
        has_numbers = bool(re.search(r'\d', size_str))
        
        if has_numbers:
            # 수치가 있는 경우 완전히 추상화
            if any(keyword in size_lower for keyword in ['×', 'x', '×', 'cm', 'mm']):
                # 치수가 있는 경우
                return "적절한 크기의 작품"
            elif 'kg' in size_lower or 'g' in size_lower:
                # 무게가 있는 경우
                return "견고한 재질"
            else:
                return "적절한 규모"
        else:
            # 이미 추상적인 표현인 경우
            if any(keyword in size_lower for keyword in ['소형', 'small', '작은']):
                return "소규모 작품"
            elif any(keyword in size_lower for keyword in ['대형', 'large', '큰']):
                return "대규모 작품" 
            elif any(keyword in size_lower for keyword in ['중형', 'medium', '중간']):
                return "중간 규모 작품"
            else:
                return "적절한 규모"
    
    def format_visitor_prompt(self, artwork: Dict[str, Any], exclude_instructions: set = None) -> str:
        """일반 관람객 관점 프롬프트 생성 (기존 질문 제외)"""
        template = self.load_prompt("visitor_questions")
        artwork_info = self._format_artwork_info(artwork)
        
        # 작가명과 작품명 정보 추출
        artist_name = artwork.get("작가", artwork.get("성명", "N/A"))
        artwork_title = artwork.get("제목", artwork.get("작품명", "N/A"))
        
        # 동적 예시 생성
        customized_format = self.json_output_format.format(
            artist_name=artist_name,
            artwork_title=artwork_title
        )
        
        base_prompt = template.format(
            artwork_info=artwork_info,
            output_format=customized_format,
            artist_name=artist_name,
            artwork_title=artwork_title
        )
        
        # 기존 질문 제외 로직 추가
        if exclude_instructions:
            exclusion_list = "\n".join([f"- {instr}" for instr in list(exclude_instructions)[:10]])  # 최대 10개
            exclusion_note = f"""

### 중요: 다음 질문들과 유사하지 않도록 완전히 다른 질문을 생성해주세요:
{exclusion_list}
위 질문들과 비슷하거나 중복되는 내용은 피해주세요.
"""
            return base_prompt + exclusion_note
        
        return base_prompt
    
    def format_curator_artwork_prompt(self, artwork: Dict[str, Any], exclude_instructions: set = None) -> str:
        """큐레이터 관점 작품 프롬프트 생성"""
        template = self.load_prompt("curator_artwork_questions")
        artwork_info = self._format_artwork_info(artwork)
        
        # 작가명과 작품명 정보 추출
        artist_name = artwork.get("작가", artwork.get("성명", "N/A"))
        artwork_title = artwork.get("제목", artwork.get("작품명", "N/A"))
        
        # 동적 예시 생성
        customized_format = self.json_output_format.format(
            artist_name=artist_name,
            artwork_title=artwork_title
        )
        
        base_prompt = template.format(
            artwork_info=artwork_info,
            output_format=customized_format,
            artist_name=artist_name,
            artwork_title=artwork_title
        )
        
        # 기존 질문 제외 로직 추가
        if exclude_instructions:
            exclusion_list = "\n".join([f"- {instr}" for instr in list(exclude_instructions)[:10]])  # 최대 10개
            exclusion_note = f"""

### 중요: 다음 질문들과 유사하지 않도록 완전히 다른 질문을 생성해주세요:
{exclusion_list}
위 질문들과 비슷하거나 중복되는 내용은 피해주세요.
"""
            return base_prompt + exclusion_note
        
        return base_prompt
    
    def format_curator_artist_prompt(self, artwork: Dict[str, Any], exclude_instructions: set = None) -> str:
        """큐레이터 관점 작가 프롬프트 생성"""
        template = self.load_prompt("curator_artist_questions")
        
        # 작가명 추출
        artist_name = artwork.get("작가", artwork.get("성명", "N/A"))
        
        # 작가 정보 필드 가져오기 (전시/수상 이력에서 수치 제거)
        education = artwork.get("학력", "N/A")
        exhibitions_raw = artwork.get("전시이력", []) or artwork.get("주요전시경력", "N/A")
        awards_raw = artwork.get("수상이력", []) or artwork.get("수상경력", "N/A")
        
        # 전시/수상 이력 필터링 (연도는 보존, 구체적 수치만 제거)
        exhibitions = self._filter_exhibition_awards_content(exhibitions_raw)
        awards = self._filter_exhibition_awards_content(awards_raw)
        
        # 작가 활동 정보 구성
        activities = f"주요 작업 분야: {artwork.get('기법', 'N/A')}\n"
        materials = artwork.get('재료') or artwork.get('소재') or artwork.get('소재 번역', 'N/A')
        activities += f"대표 소재: {materials}"
        
        # 작가 정보 포맷
        artist_info = self.artist_info_template.format(
            artist_name=artist_name,
            nationality=artwork.get("국적", "N/A"),
            birth_year=artwork.get("출생년도", "N/A"),
            education=education,
            major_exhibitions=exhibitions,
            awards=awards,
            artist_activities=activities
        )
        
        # 동적 예시 생성 (작가 프롬프트는 작품명 대신 작가명만)
        customized_format = self.json_output_format.format(
            artist_name=artist_name,
            artwork_title="[작품명]"  # 작가 질문에서는 일반적 표현
        )
        
        base_prompt = template.format(
            artist_info=artist_info,
            output_format=customized_format,
            artist_name=artist_name
        )
        
        # 기존 질문 제외 로직 추가
        if exclude_instructions:
            exclusion_list = "\n".join([f"- {instr}" for instr in list(exclude_instructions)[:10]])  # 최대 10개
            exclusion_note = f"""

### 중요: 다음 질문들과 유사하지 않도록 완전히 다른 질문을 생성해주세요:
{exclusion_list}
위 질문들과 비슷하거나 중복되는 내용은 피해주세요.
"""
            return base_prompt + exclusion_note
        
        return base_prompt
    
    def clear_cache(self):
        """프롬프트 캐시 초기화"""
        self._cache.clear()
    
    def reload_prompt(self, prompt_name: str):
        """특정 프롬프트 다시 로드"""
        if prompt_name in self._cache:
            del self._cache[prompt_name]
        return self.load_prompt(prompt_name)


# 전역 인스턴스
_prompt_loader = None

def get_prompt_loader() -> PromptLoader:
    """프롬프트 로더 인스턴스 반환 (싱글톤)"""
    global _prompt_loader
    if _prompt_loader is None:
        _prompt_loader = PromptLoader()
    return _prompt_loader