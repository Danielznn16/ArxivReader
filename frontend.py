import streamlit as st
st.set_page_config(layout="wide")
from mongo import arxiv_db

user_name = "owner"

def getDates():
    user = st.text_input("用户名称")
    if user==user_name:
        unreadOnly = st.checkbox("是否只查看未读的",value=True)
    else:
        unreadOnly = False
    if unreadOnly:
        dates = sorted(arxiv_db.find({"Read":{"$exists":False}}).distinct("email_date"),reverse=False)
    else:
        dates = sorted(arxiv_db.find({}).distinct("email_date"),reverse=False)
    k = st.select_slider("选择日期",dates,value=dates[-1])
    return k,unreadOnly,user

def MarkRead(paper_id):
    arxiv_db.update_one(dict(_id=paper_id),{"$set":{"Read":True}})

def MarkGood(paper_id):
    arxiv_db.update_one(dict(_id=paper_id),{"$set":{"Read":"good"}})

def getPapers(date,unreadOnly,user):
    query = dict(email_date=date)
    is_first = True
    papers = list(arxiv_db.find(query))
    read_cnt = 0
    total = len(papers)
    progress = st.progress(0,text=f"{0} Read in {total}")
    for paper in papers:
        if "Read" in paper:
            read_cnt+=1
            progress.progress(read_cnt/total,f"{read_cnt} Read in {total}")
            if unreadOnly:
                continue
            if paper["Read"]=="Good":
                paper["title"] = "\\[Good\\] "+f"*{paper['title']}*"
            else:
                paper["title"] = "\\[已读\\] "+f"*{paper['title']}*"
        else:
            paper["title"] = "\\[未读\\] "+f"*{paper['title']}*"
        with st.expander(paper["title"],is_first):
            is_first = False
            paper_id = paper["_id"]
            if user!=user_name:
                continue
            l,r=st.columns(2)
            l.button(
                "Mark → 已读",
                on_click=MarkRead,
                key=paper["link"]+"read",
                use_container_width=True,
                kwargs=dict(paper_id=paper_id),
                disabled=("Read" in paper)
                )
            r.button(
                "Mark → Good",
                on_click=MarkGood,
                key=paper["link"]+"good",
                use_container_width=True,
                kwargs=dict(paper_id=paper_id),
                disabled=("Read" in paper and paper["Read"]=="Good")
                )
            for key,value in sorted(list(paper.items()),key=lambda x:x[0]):
                if key in ["_id","link","email_date","title","cs","Read"]:
                    continue
                st.markdown(f"###### {key}")
                if key=="abstract":
                    value = value.replace(". ",".\n\n")
                st.markdown(
                    value,
                    unsafe_allow_html=True)
            if "cs" in paper:
                st.markdown(f"###### tags(under cs)")
                st.markdown(', '.join(list(paper["cs"].keys())))
            st.markdown("###### [View in arXiv]({})".format(paper["link"].replace("abs","pdf")+".pdf"))
date,unreadOnly,user = getDates()
getPapers(date,unreadOnly,user)
