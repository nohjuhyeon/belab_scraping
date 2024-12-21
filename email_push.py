import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os 
from g2b_notice_check.g2b_notice import notice_collection
from g2b_notice_check.g2b_preparation import preparation_collection
from g2b_notice_check.google_sheet_send import google_sheet_update
from g2b_notice_check.mongodb_update import mongodb_update
from dotenv import load_dotenv
import logging
from datetime import datetime

def html_content_write(html_content, sorted_notices, notice_type):
    html_content += "<h4>{} {}건</h4>".format(notice_type, len(sorted_notices))
    html_content += """
    <table border='1' style='border-collapse: collapse; width: 1220px; margin-bottom: 20px;'>
        <tr>
            <th style='padding: 10px; width: 6%; text-align: center;'>번호</th>
            <th style='padding: 10px; width: 30%; text-align: center;'>공고명</th>
            <th style='padding: 10px; width: 11%; text-align: center;'>추정 가격</th>
            <th style='padding: 10px; width: 16%; text-align: center;'>공고 기관</th>
            <th style='padding: 10px; width: 14%; text-align: center;'>공고 기간</th>
            <th style='padding: 10px; width: 16%; text-align: center;'>수요 기관</th>
            <th style='padding: 10px; width: 7%; text-align: center;'>링크</th>
        </tr>
    """
    list_count = 0 
    for i in sorted_notices:
        list_count += 1
        if i['new']==True:
            html_content += "<tr style='background-color:  #e0f7fa; color: black;'>"
            html_content += "<td style='padding: 10px; width: 6%; text-align: center;'><strong>{}</strong></td>".format(str(list_count)+'(new!)')
            html_content += "<td style='padding: 10px; width: 30%; text-align: center;'><strong>{}</strong></td>".format(i['title'])
            html_content += "<td style='padding: 10px; width: 11%; text-align: center;'><strong>{}</strong></td>".format(i['price'])
            html_content += "<td style='padding: 10px; width: 16%; text-align: center;'><strong>{}</strong></td>".format(i['publishing_agency'])
            html_content += "<td style='padding: 10px; width: 14%; text-align: center;'><strong>개시일 : {}<br>마감일 : {}</strong></td>".format(i['start_date'], i['end_date'])
            html_content += "<td style='padding: 10px; width: 16%; text-align: center;'><strong>{}</strong></td>".format(i['requesting_agency'])
            html_content += "<td style='padding: 10px; width: 7%; text-align: center;'><a href='{}'><strong>바로가기</strong></a></td>".format(i['link'])
        else:                
            html_content += "<tr>"
            html_content += "<td style='padding: 10px; width: 6%; text-align: center;'>{}</td>".format(list_count)
            html_content += "<td style='padding: 10px; width: 30%; text-align: center;'>{}</td>".format(i['title'])
            html_content += "<td style='padding: 10px; width: 11%; text-align: center;'>{}</td>".format(i['price'])
            html_content += "<td style='padding: 10px; width: 16%; text-align: center;'>{}</td>".format(i['publishing_agency'])
            html_content += "<td style='padding: 10px; width: 14%; text-align: center;'>개시일 : {}<br>마감일 : {}</td>".format(i['start_date'], i['end_date'])
            html_content += "<td style='padding: 10px; width: 16%; text-align: center;'>{}</td>".format(i['requesting_agency'])
            html_content += "<td style='padding: 10px; width: 7%; text-align: center;'><a href='{}'>바로가기</a></td>".format(i['link'])
        html_content += "</tr>"
    html_content += "</table>"
    return html_content

def html_create(html_content, ai_list, check_list, notice_type):
    html_content += "<h3>{}: AI관련 공고 {}건, 확인이 필요한 공고 {}건이 올라왔습니다.</h3>".format(notice_type, len(ai_list), len(check_list))
    if len(ai_list) > 0:
        sorted_notices = sorted(ai_list,key=lambda x: datetime.strptime(x["start_date"], "%Y/%m/%d"),reverse=True)
        html_content = html_content_write(html_content, sorted_notices,'AI 관련 공고')
    if len(check_list) > 0:
        sorted_notices = sorted(check_list,key=lambda x: datetime.strptime(x["start_date"], "%Y/%m/%d"),reverse=True)
        html_content = html_content_write(html_content, sorted_notices,'확인이 필요한 공고')
    return html_content


def email_sending():
    print('나라장터 공고를 찾습니다.')
    ai_notice_list, check_notice_list = notice_collection()
    ai_preparation_list, check_preparation_list = preparation_collection()
    gmail_user = 'jh.belab@gmail.com'
    gmail_password = os.environ.get("gmail_password")
    print('이메일을 보내겠습니다.')

    sender_email = 'jh.belab@gmail.com'
    receiver_email_list = ['jh.noh@belab.co.kr']
    receiver_email = 'jh.noh@belab.co.kr'
    subject = '나라장터에 새로운 ISP 공고가 올라왔습니다.'
    if len(ai_notice_list) > 0 or len(check_notice_list) > 0 or len(ai_preparation_list) > 0 or len(check_preparation_list) > 0:
        html_content = '<h2>나라장터에 새로 올라온 ISP공고가 있습니다. 확인 부탁드립니다.</h2>'
        if len(ai_notice_list) > 0 or len(check_notice_list) > 0:
            html_content = html_create(html_content, ai_notice_list, check_notice_list, '입찰 공고')
            
        if len(ai_preparation_list) > 0 or len(check_preparation_list) > 0:
            html_content = html_create(html_content, ai_preparation_list, check_preparation_list, '사전 규격')

        for receiver_email in receiver_email_list:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = sender_email
            message['To'] = receiver_email

            part1 = MIMEText(html_content, 'html')
            message.attach(part1)

            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(sender_email, receiver_email, message.as_string())
                server.quit()
                print("메일이 성공적으로 발송되었습니다.")
            except Exception as e:
                print(f"메일 발송 중 오류 발생: {e}")
    else:
        print('새로운 공고가 없습니다.')


try:
    print("----------------공고 확인 시작----------------")
    print(datetime.now())
    load_dotenv()
    folder_path = os.environ.get("folder_path")
    logging.basicConfig(filename=folder_path+'/log_list/scheduler.txt', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("----------------notice check started----------------") # 스케줄러 시작 로그 기록
    email_sending()
    mongodb_update()
    google_sheet_update()
    # 스크립트 경로와 인자 설정
except (KeyboardInterrupt, SystemExit):
    print("notice check shut down.")
    logging.info("notice check shut down.") # 스케줄러 종료 로그 기록
finally:
    print("공고 확인 완료!")



