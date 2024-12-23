import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os 
from datetime import datetime
from function_list.basic_options import mongo_setting
import pandas as pd 
from datetime import datetime, timedelta


def html_content_write(html_content, sorted_notices, notice_type):
    sorted_notices = sorted_notices.to_dict(orient='records')
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

def html_create(html_content, ai_list,db_list, check_list, notice_type,user_type):
    if user_type == 'all':
        html_content += "<h3>{}: AI관련 공고 {}건, DB 관련 공고 {},확인이 필요한 공고 {}건이 올라왔습니다.</h3>".format(notice_type, len(ai_list),len(db_list), len(check_list))
        if len(ai_list) > 0:
            sorted_notices = ai_list.sort_values(by='start_date_sort', ascending=False).reset_index(drop=True)

            html_content = html_content_write(html_content, sorted_notices,'AI 관련 공고')
        if len(db_list) > 0:
            sorted_notices = db_list.sort_values(by='start_date_sort', ascending=False).reset_index(drop=True)
            html_content = html_content_write(html_content, sorted_notices,'DB 관련 공고')
        if len(check_list) > 0:
            sorted_notices = check_list.sort_values(by='start_date_sort', ascending=False).reset_index(drop=True)
            html_content = html_content_write(html_content, sorted_notices,'확인이 필요한 공고')

    elif user_type == 'ai':
        html_content += "<h3>{}: AI관련 공고 {}건이 올라왔습니다.</h3>".format(notice_type, len(ai_list))
        if len(ai_list) > 0:
            sorted_notices = ai_list.sort_values(by='start_date_sort', ascending=False).reset_index(drop=True)
            html_content = html_content_write(html_content, sorted_notices,'AI 관련 공고')
    elif user_type == 'db':
        html_content += "<h3>{}: DB 관련 공고 {}이 올라왔습니다.</h3>".format(notice_type, len(db_list))
        if len(db_list) > 0:
            sorted_notices = db_list.sort_values(by='start_date_sort', ascending=False).reset_index(drop=True)
            html_content = html_content_write(html_content, sorted_notices,'DB 관련 공고')
    return html_content


def email_push(notice_list,user_type):
    gmail_user = 'jh.belab@gmail.com'
    gmail_password = os.environ.get("gmail_password")
    print('이메일을 보내겠습니다.')

    sender_email = 'jh.belab@gmail.com'
    receiver_email_list = ['jh.noh@belab.co.kr']
    receiver_email = 'jh.noh@belab.co.kr'
    subject = '나라장터에 새로운 ISP 공고가 올라왔습니다.'
    class_list = ['입찰 공고','사전 규격']
    if len(notice_list)> 0:
        html_content = '<h2>나라장터에 새로 올라온 ISP공고가 있습니다. 확인 부탁드립니다.</h2>'
        for i in class_list:
            ai_notice_list = notice_list.loc[(notice_list['notice_class']==i)&(notice_list['type'].str.contains('인공 지능'))]
            db_notice_list = notice_list.loc[(notice_list['notice_class']==i)&(notice_list['type'].str.contains('데이터베이스'))]
            check_notice_list = notice_list.loc[(notice_list['notice_class']==i)&(notice_list['type'].str.contains('검토 필요'))]
            html_content = html_create(html_content, ai_notice_list,db_notice_list,check_notice_list, i,user_type)

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



def email_sending():
    collection = mongo_setting('news_scraping','notice_list')
    # 모든 문서 가져오기
    documents = collection.find()

    # DataFrame으로 변환
    df = pd.DataFrame(list(documents))
    df['start_date_sort'] = pd.to_datetime(df['start_date'], format='%Y/%m/%d')

    # 최신 순으로 정렬

    yesterday = datetime.now() - timedelta(days=1)
    today = datetime.now()
    yesterday = yesterday.strftime('%Y/%m/%d')
    today = today.strftime('%Y/%m/%d')
    df=df.loc[(df['start_date_sort']==today)|(df['start_date_sort']==yesterday)]
    if len(df)>0:
        email_push(df,'all')

        notice_list = df.loc[df['type'].str.contains('인공 지능')]
        if len(notice_list)>0:
            email_push(notice_list,'ai')
        notice_list = df.loc[df['type'].str.contains('데이터베이스')]
        if len(notice_list)>0:
            email_push(notice_list,'db')

