from function_list.hwp_loader import HWPLoader

# HWP Loader 객체 생성
loader = HWPLoader("./test.hwp")

# 문서 로드
docs = loader.load()
print(docs[0].page_content)
pass