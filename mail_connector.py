import email
from email.utils import parseaddr
import imaplib
from email.header import decode_header
import os
import time
import requests

user = input("Email User Name:\n").strip()
passd = input("Email Password:\n").strip()
imap_server = input("Email IMAP SERVER Address:\n").strip()

def loop_check(targetBox):
    server = imaplib.IMAP4_SSL(imap_server)

    server.login(user,passd)
    rsp, box = server.select(targetBox)
    assert(rsp=="OK")
    
    type, data = server.search(None, "UNSEEN") # None stands for ascii
    indexs = data[0].split()
    print(f"{targetBox} has {len(indexs)} unresolved mails")
    for i in indexs:
        # server.store(i,'-FLAGS','\\SEEN') # Set as un-read
        # continue
        try:
            type, datas = server.fetch(i,'(RFC822)')
            text = datas[0][1].decode('utf8')
            server.store(i,'+FLAGS','\\SEEN')
        except:
            continue
        msg = email.message_from_string(text)

        From = parseaddr(msg.get('from'))[1]
        To = parseaddr(msg.get('To'))[1]
        CC = parseaddr(msg.get_all('Cc'))[1]
        Subject = decode_str(parseaddr(msg.get('Subject'))[1])
        date1 = time.strptime(msg.get("Date")[0:24],'%a, %d %b %Y %H:%M:%S')
        date2 = time.strftime("%Y-%m-%d",date1)
        print(f'From: {From} To: {To} Date: {date2}')
        content = ""
        for part in msg.walk():
            file_name = part.get_filename()
            if file_name:
                file_name = decode_str(file_name)
                # data = part.get_payload(decode=True)
                # # Save the file
                # att_file = open(os.path.join(save_path, file_name), 'wb')
                # attachment_files.append(file_name)
                # att_file.write(data)
                # att_file.close()
            elif not part.is_multipart():
                content+=part.get_payload(decode=True).decode('utf-8')
        yield dict(
            fr=From,
            to=To,
            cc=CC,
            subject=Subject,
            date_short=date2,
            date_full = date1,
            content=content
        )

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
        return value
