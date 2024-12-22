import olefile
import zlib
import struct
import zipfile
import xml.etree.ElementTree as ET


def detect_file_type(file_path):
    try:
        with open(file_path, 'rb') as f:
            # 파일의 처음 8바이트 읽기
            header = f.read(8)
            
            # HWP 파일 확인 (OLE2 매직 넘버)
            if header.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
                content = get_hwp_text(file_path)
                return content
            
            # HWPX 파일 확인 (ZIP 매직 넘버)
            elif header.startswith(b'\x50\x4B\x03\x04'):
                content = get_hwpx_text(file_path)
                return content
            
            # 기타 파일
            else:
                return "Unknown"
    except Exception as e:
        return f"Error detecting file type: {e}"


def get_hwp_text(filename):
    try:
        with olefile.OleFileIO(filename) as f:
            dirs = f.listdir()

            # HWP 파일 검증
            if ["FileHeader"] not in dirs or ["\x05HwpSummaryInformation"] not in dirs:
                print("Not a valid HWP file.")
                return None

            # 문서 포맷 압축 여부 확인
            header = f.openstream("FileHeader")
            header_data = header.read()
            is_compressed = (header_data[36] & 1) == 1

            # Body Sections 불러오기
            nums = []
            for d in dirs:
                if d[0] == "BodyText":
                    nums.append(int(d[1][len("Section"):]))
            sections = ["BodyText/Section" + str(x) for x in sorted(nums)]

            # 전체 text 추출
            text = ""
            for section in sections:
                bodytext = f.openstream(section)
                data = bodytext.read()
                if is_compressed:
                    unpacked_data = zlib.decompress(data, -15)
                else:
                    unpacked_data = data

                # 각 Section 내 text 추출    
                section_text = ""
                i = 0
                size = len(unpacked_data)
                while i < size:
                    header = struct.unpack_from("<I", unpacked_data, i)[0]
                    rec_type = header & 0x3ff
                    rec_len = (header >> 20) & 0xfff

                    if rec_type in [67]:
                        rec_data = unpacked_data[i+4:i+4+rec_len]
                        section_text += rec_data.decode('utf-16', errors='ignore')
                        section_text += "\n"

                    i += 4 + rec_len

                text += section_text
                text += "\n"

            return text
    except Exception as e:
        print(e)
        return None


def get_hwpx_text(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            # Contents 폴더 내의 섹션 파일 목록 찾기
            section_files = [name for name in zf.namelist() if name.startswith('Contents/section') and name.endswith('.xml')]

            # 모든 섹션 파일의 텍스트를 저장할 리스트
            all_texts = []

            for section_file in section_files:
                with zf.open(section_file) as file:
                    tree = ET.parse(file)
                    root = tree.getroot()

                    # 현재 섹션의 텍스트 추출
                    for elem in root.iter():
                        if elem.tag.endswith('t'):  # 텍스트 태그 확인
                            if elem.text:
                                all_texts.append(elem.text.strip())

            # 모든 섹션 텍스트를 하나로 합치기
            return ' '.join(all_texts)
    except Exception as e:
        return f"Error extracting text: {e}"




# 사용 예시
file_path = "test_1.hwp"  # 또는 "example.hwpx"
content = detect_file_type(file_path)
# print(f"The file type is: {file_type}")
print(content)

# # 사용 예시
# file_path = "test_1.hwp"  # 또는 "example.hwpx"
# content = get_hwp_text(file_path)
# print(content)
# 