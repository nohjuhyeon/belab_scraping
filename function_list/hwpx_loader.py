import zipfile
import os
import zipfile
import xml.etree.ElementTree as ET

def get_hwpx_text(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            # Contents 폴더 내의 섹션 파일 목록 찾기
            section_files = [name for name in zf.namelist() if name.startswith('Contents/section') and name.endswith('.xml')]

            # 모든 섹션 파일의 텍스트를 저장할 리스트
            output_dir = "extracted_sections"
            os.makedirs(output_dir, exist_ok=True)  # 디렉토리가 없으면 생성
            metadata = {}
            docs = []
            for section_file in section_files:
                with zf.open(section_file) as section_file_content:
                    # 파일 내용 읽기
                    section_content = section_file_content.read().decode('utf-8')

                    # # XML 파일로 저장
                    # output_file_path = os.path.join(output_dir, os.path.basename(section_file))
                    # with open(output_file_path, "w", encoding="utf-8") as output_file:
                    #     output_file.write(section_content)

                    # print(f"파일 저장됨: {output_file_path}")

                root = ET.fromstring(section_content)           
                # 네임스페이스 정의
                pages = []
                current_page = []

                table_texts = []
                for tbl in root.findall(".//hp:tbl", namespaces={"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}):
                    table_texts.extend(
                        [t.text for t in tbl.findall(".//hp:t", namespaces={"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}) if t.text]
                    )

                for p in root.findall(".//hp:p", namespaces={"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"}):
                    # pageBreak 속성 확인
                    page_break = p.attrib.get("pageBreak", "0")  # pageBreak 속성 가져오기
                    text_elements = p.findall(".//hp:t", namespaces={"hp": "http://www.hancom.co.kr/hwpml/2011/paragraph"})
                    text = " ".join([t.text for t in text_elements if t.text and t.text not in table_texts])  # 테이블 텍스트 제외

                    if page_break == "1":  # 새로운 페이지 시작
                        if current_page:
                            pages.append(current_page)  # 이전 페이지 저장
                        current_page = []  # 새로운 페이지 초기화

                    if text:  # 텍스트가 있으면 추가
                        current_page.append(text)

                # 마지막 페이지 저장
                if current_page:
                    pages.append(current_page)

                # 결과 출력
                for i, page in enumerate(pages, start=1):
                    text = "\n".join(page)
                    docs.append(text)
            for idx in range(len(docs)):
                section_name = f"section{idx}"  # 섹션 이름 생성 (section1, section2, ...)
                metadata[section_name] = docs[idx]  # 메타데이터에 저장

            # 모든 섹션 텍스트를 하나로 합치기
            return docs, metadata
    except Exception as e:
        return f"Error extracting text: {e}"
