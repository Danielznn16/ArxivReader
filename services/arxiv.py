from mail_connector import loop_check
from mongo import arxiv_db

def checkArxiv():
    for mail in loop_check("Arxiv"):
        _, header, main_content = mail['content'].split("------------------------------------------------------------------------------\r\n------------------------------------------------------------------------------")
        new_content, update_content = main_content.split("%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%--%%")
        single_listing_content, cross_listing_content = new_content.split("%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-%-")
        contents = dict(
            single_new = single_listing_content,
            cross_new = cross_listing_content,
            update = update_content
        )
        email_date = mail["date_short"]
        for content_type,content in contents.items():
            if content_type=="update":
                continue
            content = content.split("------------------------------------------------------------------------------")
            content = [i.strip() for i in content]
            content = [i for i in content if i]
            content = content[1:]
            for paper in content:
                try:
                    _, paperHeader, paperAbs, link = paper.split('\\\\')
                except:
                    paper = paper[2:]
                    paperHeader, paperAbs, link = paper.split("\r\n\\\\")
                # Parse Header
                paperHeader = [i for i in paperHeader.strip().split('\r\n') if i.strip()]
                paperHeaderDict = []
                for line in paperHeader:
                    if line.startswith("arXiv:"):
                        paperHeaderDict.append(["id",line.split(' ')[0]])
                    elif line.startswith("Date:"):
                        paperHeaderDict.append(["date",line.split('(')[0].strip()[6:]])
                    elif line.startswith("Title:"):
                        paperHeaderDict.append(["title",line[7:]])
                    elif line.startswith("Authors:"):
                        paperHeaderDict.append(["authors",line[9:]])
                    elif line.startswith("Categories:"):
                        paperHeaderDict.append(["categories",line[12:]])
                    elif line.startswith("Comments:"):
                        paperHeaderDict.append(["comment",line[10:]])
                    elif line[0]==' ':
                        paperHeaderDict[-1][1]+=line
                    else:
                        line = line.split(':')
                        tag, line = line[0],':'.join(line[1:])
                        paperHeaderDict.append([tag,line])
                paperHeaderDict = {i[0]:i[1].strip() for i in paperHeaderDict}
                categories = paperHeaderDict["categories"].split(' ')
                del paperHeaderDict["categories"]
                for cat in categories:
                    paperHeaderDict[cat] = True
                
                # Parse Abs
                paperAbs = paperAbs.replace('\r\n',' ').strip()

                # Parser paper url
                link = link.strip().split(',')[0][2:].strip()
                
                writePaper(email_date = email_date, abstract=paperAbs,link = link, **paperHeaderDict)

def writePaper(link, **kwargs):
    kwargs['link'] = link
    arxiv_db.update_one(
        dict(
            link=link
        ),
        {"$set":kwargs},
        upsert=True
        )