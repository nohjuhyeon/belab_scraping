import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os 
import pandas as pd 
from datetime import datetime

def notice_date_modify(date_time):
    """
    날짜 문자열을 특정 형식으로 변환합니다.
    :param date_time: 입력 날짜 문자열
    :return: 변환된 날짜 (datetime 형식)
    """
    try:
        new_date = pd.to_datetime(date_time, format='%Y-%m-%d %H:%M:%S')
    except:
        new_date = pd.to_datetime(date_time, format='%Y-%m-%d')
    return new_date

def html_content_write(html_content, notice_elements, notice_class):
    """
    공고 데이터를 기반으로 HTML 테이블 형식의 콘텐츠를 작성합니다.
    :param html_content: 기존 HTML 콘텐츠 문자열
    :param notice_elements: 공고 데이터를 포함한 DataFrame
    :param notice_class: 공고 유형 (예: '입찰 공고', '사전 규격')
    :return: HTML 콘텐츠 문자열
    """
    # DataFrame을 딕셔너리 리스트로 변환
    notice_elements = notice_elements.to_dict(orient='records')
    
    # HTML 콘텐츠 초기화 및 헤더 추가
    html_content += '<hr>'
    html_content += "<h4>{}: {}건</h4>".format(notice_class, len(notice_elements))
    html_content += """
    <table border='1' style='border-collapse: collapse; width: 90%; margin-bottom: 20px;'>
        <tr>
            <th style='padding: 10px; width: 5%; text-align: center;'>번호</th>
            <th style='padding: 10px; width: 22%; text-align: center;'>공고명</th>
            <th style='padding: 10px; width: 11%; text-align: center;'>추정 가격</th>
            <th style='padding: 10px; width: 15%; text-align: center;'>공고 기관</th>
            <th style='padding: 10px; width: 14%; text-align: center;'>공고 기간</th>
            <th style='padding: 10px; width: 15%; text-align: center;'>수요 기관</th>
            <th style='padding: 10px; width: 7%; text-align: center;'>링크</th>
            <th style='padding: 10px; width: 11%; text-align: center;'>비고</th>
        </tr>
    """
    
    # 공고 데이터 행 추가
    list_count = 0 
    for i in notice_elements:
        list_count += 1
        html_content += "<tr>"
        html_content += "<td style='padding: 10px; text-align: center;'>{}</td>".format(list_count)
        html_content += "<td style='padding: 10px; text-align: center;'>{}</td>".format(i['공고명'])
        html_content += "<td style='padding: 10px; text-align: center;'>{}</td>".format(i['공고가격(단위: 원)'])
        html_content += "<td style='padding: 10px; text-align: center;'>{}</td>".format(i['공고 기관'])
        html_content += "<td style='padding: 10px; text-align: center;'>개시일 : {}<br>마감일 : {}</td>".format(i['게시일'], i['마감일'])
        html_content += "<td style='padding: 10px; text-align: center;'>{}</td>".format(i['수요 기관'])
        html_content += "<td style='padding: 10px; text-align: center;'><a href='{}'>바로가기</a></td>".format(i['링크'])
        html_content += "<td style='padding: 10px; text-align: center;'>{}</td>".format(i['비고'])
        html_content += "</tr>"
    html_content += "</table>"
    return html_content

def html_create(html_content, notice_elements, notice_class):
    """
    HTML 콘텐츠를 생성합니다.
    :param html_content: 기존 HTML 콘텐츠 문자열
    :param notice_elements: 공고 데이터를 포함한 DataFrame
    :param notice_class: 공고 유형 (예: '입찰 공고', '사전 규격')
    :return: HTML 콘텐츠 문자열
    """
    html_content = html_content_write(html_content, notice_elements, notice_class)
    return html_content

def email_push(notice_list, email_list, notice_link, notice_type):
    """
    이메일을 통해 공고 알림을 발송합니다.
    :param notice_list: 공고 데이터를 포함한 DataFrame
    :param email_list: 이메일 수신자 리스트
    :param notice_link: 공고 관련 링크
    :param notice_type: 공고 유형 (예: '입찰 공고')
    """
    today_date = datetime.now().strftime('%Y년 %m월 %d일')

    # 메일 계정 정보 설정
    mailplug_user = 'jh.noh@belab.co.kr'
    mailplug_password = os.environ.get("mailplug_password")
    
    sender_email = 'jh.noh@belab.co.kr'
    subject = '나라장터에 새로운 {} 공고가 올라왔습니다.'.format(notice_type)
    class_list = ['입찰 공고', '사전 규격']

    if len(notice_list) > 0:
        # 이메일 본문 초기화
        html_content = '<h2>나라장터에 새로 올라온 {} 공고가 있습니다. 확인 부탁드립니다.({} 8:00 기준)</h2>'.format(notice_type, today_date)
        html_content += '<h4>더 많은 공고는 아래 링크를 참고해주세요.</h4>'
        html_content += '<ul style="list-style-type: disc; padding-left: 20px;"><li><a href="{0}" target="_blank">{0}</a></li></ul>'.format(notice_link)

        # 공고 유형별로 HTML 콘텐츠 작성
        for i in class_list:
            notice_elements = notice_list.loc[(notice_list['공고 유형'] == i)]
            notice_elements = notice_elements.copy()  # 복사본 생성
            notice_elements['게시일_sort'] = notice_elements['게시일'].apply(notice_date_modify)
            notice_elements['게시일'] = notice_elements['게시일'].fillna('').astype(str).str.split(' ').str[0]
            notice_elements['마감일'] = notice_elements['마감일'].fillna('').astype(str).str.split(' ').str[0]
            notice_elements = notice_elements.sort_values(by='게시일_sort', ascending=False)
            notice_elements = notice_elements.drop_duplicates(subset='공고명', keep='first').reset_index(drop=True)

            html_content = html_create(html_content, notice_elements, i)

        # 이메일 발송
        for receiver_email in email_list:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = sender_email
            message['To'] = receiver_email

            part1 = MIMEText(html_content, 'html')
            message.attach(part1)

            try:
                server = smtplib.SMTP_SSL('smtp.mailplug.co.kr', 465)
                server.ehlo()
                server.login(mailplug_user, mailplug_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
                server.quit()
                print("{} 메일이 성공적으로 발송되었습니다.".format(notice_type))
            except Exception as e:
                print(f"메일 발송 중 오류 발생: {e}")
    else:
        print('새로운 공고가 없습니다.')

def email_sending(notice_list, email_list, notice_link, notice_class):
    """
    공고 알림 이메일 발송을 실행합니다.

    Args:
        notice_list (DataFrame): 공고 데이터를 포함한 데이터프레임
        email_list (List[str]): 이메일 수신자 리스트
        notice_link (str): 공고 관련 링크
        notice_class (str): 공고 유형 (예: '입찰 공고')
    """
    if len(notice_list) > 0:
        email_push(notice_list, email_list, notice_link, notice_class)
