import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os 
import pandas as pd 
from datetime import datetime, timedelta


def html_content_write(html_content, notice_elements,notice_class):
    notice_elements = notice_elements.to_dict(orient='records')
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

    html_content = html_content_write(html_content, notice_elements,notice_class)
    return html_content


def email_push(notice_list,email_list,notice_link,notice_type):
    gmail_user = 'jh.belab@gmail.com'
    gmail_password = os.environ.get("gmail_password")

    sender_email = 'jh.belab@gmail.com'
    receiver_email = 'jh.noh@belab.co.kr'
    subject = '나라장터에 새로운 {} 공고가 올라왔습니다.'.format(notice_type)
    class_list = ['입찰 공고','사전 규격']
    if len(notice_list)> 0:
        html_content = '<h2>나라장터에 새로 올라온 {} 공고가 있습니다. 확인 부탁드립니다.</h2>'.format(notice_type)
        html_content += '<h4>더 많은 공고는 아래 링크를 참고해주세요.</h4>'
        html_content += '<ul style="list-style-type: disc; padding-left: 20px;"><li><a href="{0}" target="_blank">{0}</a></li></ul>'.format(notice_link)
        for i in class_list:
            notice_elements = notice_list.loc[(notice_list['공고 유형']==i)]
            notice_elements = notice_elements.copy()  # 복사본 생성
            notice_elements.loc[:, '게시일_sort'] = pd.to_datetime(notice_elements['게시일'], format='%Y-%m-%d')
            notice_elements = notice_elements.sort_values(by='게시일_sort', ascending=False).reset_index(drop=True)

            html_content = html_create(html_content, notice_elements, i)

        for receiver_email in email_list:
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
                print("{} 메일이 성공적으로 발송되었습니다.".format(notice_type))
            except Exception as e:
                print(f"메일 발송 중 오류 발생: {e}")
    else:
        print('새로운 공고가 없습니다.')



def email_sending(notice_list, email_list,notice_link,notice_class):
    notice_list
    if len(notice_list)>0:
        email_push(notice_list,email_list,notice_link,notice_class)


