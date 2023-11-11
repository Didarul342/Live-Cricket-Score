import requests
from django.shortcuts import render
import scrapy
from requests_html import HTMLSession
from django.http import HttpResponse
import feedparser
from bs4 import BeautifulSoup
import json


def index(request):
    if request.method == 'POST':
        link = "https://www.espncricinfo.com/scores"
        data = live_score(link)
        print(data)
        url = 'http://static.cricinfo.com/rss/livescores.xml'
        feed = feedparser.parse(url)
        return HttpResponse(json.dumps(data))
    else:
        link = "https://www.espncricinfo.com/scores"
        data = live_score(link)
        url = 'http://static.cricinfo.com/rss/livescores.xml'
        feed = feedparser.parse(url)
        return render(request, 'reader.html', {"feed": feed, "data": data})


def live_score(link):
    session = requests.Session()
    content = session.get(link, verify=False).content
    soup = BeautifulSoup(content, "html.parser")

    post = soup.find("div", {"class": "scoreCollection"})
    collection = post.find("div", {"class": "scoreCollection__content"})
    all_events = collection.findAll("div", {"class": "cscore"})
    data = []
    for rec in all_events:
        dic = {}
        teams = []
        cscore_link = rec.find("div", {"class": "cscore_link cscore_link--button"})
        dic['title'] = cscore_link.find("div", {"class": "cscore_info-overview"}).text
        dic['date'] = cscore_link.find("span", {"class": "cscore_date"}).text
        url = cscore_link.find("a", {"class": "cscore_details"})
        if url:
            dic['urls'] = (url['href'])
        events = cscore_link.find("a", {"class": "cscore_details"}).find("ul")
        dic['note'] = cscore_link.find("span", {"class": "cscore_notes_game"}).text

        for i in events.find_all("li", {"class": "cscore_item"}):
            team = {}
            image = i.find("img", {"class": "cscore_image"})
            if image:
                team['image'] = (image['data-src'])
            # team['image'] = i.find("img", {"class": "cscore_image"})
            team['team_name'] = i.find("span", {"class": "cscore_name"}).text
            score = i.find("div", {"class": "cscore_score"})
            if score:
                team['score'] = i.find("div", {"class": "cscore_score"}).text
            over = i.find("span", {"class": "cscore_overs"})
            if over:
                team['over'] = i.find("span", {"class": "cscore_overs"}).text

            teams.append(team)
        dic['teams'] = teams
        data.append(dic)

    return {"data": data}


def Score(request):
    session = HTMLSession()
    link = request.POST.get("link")

    date = request.POST.get("date")
    teams = request.POST.get("teams")
    title = request.POST.get("title")
    note = request.POST.get("note")

    if teams:
        re = teams.replace("'", "\"")
        teams_s = json.loads(re)

    data = scrape(link)

    return render(request, 'Scores.html', {"data": data , "teams_s": teams_s, "date": date, "title": title, "note": note})


def scrape(link):
    session = requests.Session()

    content = session.get(link, verify=False).content
    soup = BeautifulSoup(content, "html.parser")
    page_title = soup.find("title").text
    post = soup.find("div", {"class": "cscore_link"})
    pre_coummatry = soup.find("div", {"class": ["commentary-item pre"]})
    pre_com = []
    if pre_coummatry:
        pre = pre_coummatry.find_all("p", {"class": "comment"})
        for i in pre:
            d = i.text
            pre_com.append(d)
    man_of_the_match = soup.find("div", {"class": "gp__cricket__player-match"})
    if man_of_the_match:
        man_of_the_match_jersey = man_of_the_match.find("a", {"class": "headshot-jersey-sm"})
        man_of_the_match_player_name = man_of_the_match.find("a", {"class": "gp__cricket__player-match__player__detail__link"}).text
        title_of_man_of_the_match = man_of_the_match.find("div", {"class": "gp__cricket__player-match__title"}).text
    else:
        man_of_the_match_jersey =''
        man_of_the_match_player_name =''
        title_of_man_of_the_match =''

    link = post.find("span", {"class":"cscore_date"}).text
    strt = post.find("span", {"class": "cscore_time"})
    status = ''
    if strt:
        status = post.find("span", {"class":"cscore_time"}).text
    match_no = post.find("div", {"class": "cscore_info-overview"}).text
    toss = soup.find("div", {"class": "cscore_commentary"})
    toss_win = ''
    if toss:
        toss_in = soup.find("div", {"class": "cscore_commentary"})
        toss_win = toss_in.find("span", {"class": "cscore_notes_game"}).text
    details = post.find("div", {"class":"cscore_details"}).find("ul")
    score = details.find_all("div",{"class": "cscore_score"})
    score_details =[]
    over_details = []
    for i in score:
        over_1 = i.find("span", {"class":"cscore_overs"})
        over_details.append(over_1)
    team_name = []
    flag = []
    for litag in details.find_all('li'):
        flag = litag.find("img", {"class": "cscore_image"})
        score_card = litag.find("div",{"class": "cscore_score"}).text
        score_details.append(score_card)
        team_name1 = litag.find("span", {"class": "cscore_name--long"}).text
        team_name.append(team_name1)
    info_summary = soup.find("div", {"class": "col-large"})
    content_summary = info_summary.find("div", {"class":"content"})
    over = content_summary.find("div",{"class":"time-stamp"})
    description = content_summary.find("div",{"class":"description"})
    for i in content_summary.find_all("p", {"class": "comment"}):
        print(i)
    post_summary = content_summary.find("p", {"class":"comment"})

    #nav details
    link_scorecard = []
    link_game = []
    nav_div = soup.find("nav", {"class":"game-package-nav"}).find("ul")
    for i in nav_div.find_all("li",{"class": "sub"}):
        #Live
        game = i.find("a", {"class":"game"})
        link_text = i.find("span", {"class": "link-text"}).text
        if game:
            link_text = 'live'
            link_game1 = (game["href"])
            link_game.append(link_game1)

        else:
            link_text = ''
        #scorecard
        scorecard_details = i.find("a", {"class": "scorecard"})

        if scorecard_details:
            link_text_scorecard = 'scorecard'
            link_scorecard1 = (scorecard_details["href"])
            link_scorecard.append(link_scorecard1)
        else:
            link_text_scorecard = ''



    data_table = []
    batmans = []
    bowlers = []
    current_details = []
    over_detail = []
    article = soup.find("article", {"class": ["sub-module", "scorecard"]})
    tables = article.find('table')
    if tables:
        table_body = tables.find_all('tbody')
        for i in table_body:
            rows = i.find_all('tr')
            for row in rows:
                cols = row.find_all('td')

                cols = [ele.text.strip() for ele in cols]
                data_table.append([ele for ele in cols if ele])


        count = 0
        for rec in data_table:
            if count < 2:
                batmans.append(rec)
                count = count + 1



        count_bowlers = 0
        for rec in data_table:
            count_bowlers = count_bowlers + 1
            if count_bowlers >= 3:
                if count_bowlers < 5:
                    bowlers.append(rec)



        count_current = 0
        for rec in data_table:
            count_current = count_current + 1
            if count_current == 5:
                current_details.append(rec)

            if count_current == 6:
                over_detail.append(rec)


    summary = soup.find_all("article", {"class": ["sub-module", "match-commentary"]})[3:4]
    if summary:
        for rec in summary:
            post_summary1 = rec.find_all("div", {"class":"commentary-item"})

            summary_post = []
            for i in post_summary1:
                summary_post.append(i.text)
    else:
        summary_post = ''

    inning = article.find_all("div", {"class": "scorecard-section"})
    data = {"date": link,"page_title":page_title,"status":status, "match_no": match_no, "toss_win": toss_win, "team_name": team_name, "flag": flag, "post_summary":post_summary,
            "data_table": data_table,"batmans":batmans,"bowlers":bowlers, "link_text":link_text, "link_game":link_game, "link_text_scorecard":link_text_scorecard,"link_scorecard":link_scorecard,
            "score_details":score_details,"over_details":over_details,"summary_post":summary_post, "current_details":current_details,"over_detail":over_detail,"man_of_the_match_jersey":man_of_the_match_jersey,
            "man_of_the_match_player_name":man_of_the_match_player_name,"pre_com":pre_com, "title_of_man_of_the_match":title_of_man_of_the_match }

    return data


def scorecard(request):
    link = request.POST.get("link")
    rec1 = request.POST.get("date")
    teams_s = request.POST.get("teams")
    title = request.POST.get("title")
    note = request.POST.get("note")
    page_title = request.POST.get("page_title")
    if teams_s:
        re = teams_s.replace("'", "\"")
        teams = json.loads(re)
    else:
        teams = {}

    data = score_details(link)
    return render(request, 'scorecard.html',{"data": data, "page_title":page_title, "teams": teams, "title": title, "note": note, "date": rec1})


def score_details(link):
    session = requests.Session()
    content = session.get(link, verify=False).content
    soup = BeautifulSoup(content, "html.parser")
    article = soup.find("article", {"class": ["sub-module scorecard"]})
    batmans_section = article.find("div", {"class": ["scorecard-section batsmen"]})
    flex_row = batmans_section.find_all("div", {"class": ["flex-row"]})

    # For Batmans
    batsmen_first = []
    yet = []
    totals1 = []
    for rec in flex_row:
        dic = {}
        runs = []
        wrap_batsmen = rec.find("div", {"class": ["wrap batsmen"]})
        extras = rec.find("div", {"class": ["wrap extras"]})
        if extras:
            extra = extras.findAll("div",{"class":["cell"]})
            for ex in extra:
                dic["extras"] = ex
        total = rec.find("div", {"class": ["wrap total"]})
        if total:
            totals = total.findAll("div", {"class": ["cell"]})
            for ex in totals:
                dic["total"] = ex
                d = ex.text
                totals1.append(d)
        yet_to_bat = rec.find("div", {"class": ["wrap dnb"]})
        if yet_to_bat:
            a = yet_to_bat.find("div", {"class": ["cell"]})

            for i in a:

                yet.append(i)

        if wrap_batsmen:
            batmans_name = wrap_batsmen.find("div", {"class": ["cell batsmen"]}).find("a").text
            run = wrap_batsmen.find_all("div", {"class": ["cell runs"]})
        else:
            batmans_name = ''
        commentary1 = rec.find("a", {"class": ["icon-font-before collapsed"]})
        if commentary1:
            commentary = rec.find("a", {"class": ["icon-font-before collapsed"]}).text
        else:
            commentary = ''
        dic['batmans_name'] = batmans_name
        dic['commentary'] = commentary

        for i in run:
            r = i.text
            runs.append(r)
        dic['runs'] = runs
        batsmen_first.append(dic)

    bowling_section = article.find("div", {"class": ["scorecard-section bowling"]})
    tables = bowling_section.find('table')
    bowling_first = []
    if tables:
        table_body = tables.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')

            cols = [ele.text.strip() for ele in cols]
            bowling_first.append([ele for ele in cols if ele])

    article_second = soup.findAll("article", {"class": ["sub-module scorecard"]})[1:2]
    batsmen_second = []
    total_second = []
    yet_second = []
    if article_second:
        for art in article_second:
            batmans_section_second = art.find("div", {"class": ["scorecard-section batsmen"]})
            flex_row = batmans_section_second.find_all("div", {"class": ["flex-row"]})


            for rec in flex_row:
                dic = {}
                runs = []
                wrap_batsmen = rec.find("div", {"class": ["wrap batsmen"]})
                extras = rec.find("div", {"class": ["wrap extras"]})
                if extras:
                    extra = extras.findAll("div", {"class": ["cell"]})
                    for ex in extra:
                        dic["extras"] = ex
                total = rec.find("div", {"class": ["wrap total"]})
                if total:
                    totals = total.findAll("div", {"class": ["cell"]})
                    for ex in totals:
                        dic["total"] = ex
                        d = ex.text
                        total_second.append(d)

                yet_to_bat = rec.find("div", {"class": ["wrap dnb"]})
                if yet_to_bat:
                    a = yet_to_bat.find("div", {"class": ["cell"]})

                    for i in a:
                        yet_second.append(i)

                if wrap_batsmen:
                    batmans_name = wrap_batsmen.find("div", {"class": ["cell batsmen"]}).find("a").text
                    run = wrap_batsmen.find_all("div", {"class": ["cell runs"]})
                else:
                    batmans_name = ''
                commentary1 = rec.find("a", {"class": ["icon-font-before collapsed"]})
                if commentary1:
                    commentary = rec.find("a", {"class": ["icon-font-before collapsed"]}).text
                else:
                    commentary = ''
                dic['batmans_name'] = batmans_name
                dic['commentary'] = commentary

                for i in run:
                    r = i.text
                    runs.append(r)
                dic['runs'] = runs
                batsmen_second.append(dic)

    bowling_second = []
    for re in article_second:

        bowling_section_second = re.find("div", {"class": ["scorecard-section bowling"]})
        tables = bowling_section_second.find('table')

        if tables:
            table_body = tables.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')

                cols = [ele.text.strip() for ele in cols]
                bowling_second.append([ele for ele in cols if ele])
    list_bat = []
    last_wick = []
    count = 0
    if yet:
        for i in yet:
            if count == 0 :
                b = i.text
                if b == "Fall of wickets: ":
                    count = count + 1
                    last_wick.append(b)
                else:
                    list_bat.append(b)
            else:
                b = i
                last_wick.append(b)

    list_bat_sec = []
    last_wick_sec = []
    count_sec = 0
    if yet_second:
        for i in yet_second:
            if count_sec == 0:
                b = i.text
                if b == "Fall of wickets: ":
                    count_sec = count_sec + 1
                    last_wick.append(b)
                else:
                    list_bat_sec.append(b)
            else:
                b = i
                last_wick_sec.append(b)


    data = {"batsmen_first": batsmen_first, "bowling_first":bowling_first,"batsmen_second":batsmen_second, "bowling_second":bowling_second ,"yet":yet,"list_bat":list_bat,"last_wick":last_wick ,"totals":totals1, "total_second":total_second,
            "list_bat_sec": list_bat_sec, "last_wick_sec":last_wick_sec}
    return data


def schedule(request):
    link = "http://www.espncricinfo.com/ci/content/match/fixtures_futures.html"
    data = schedule_details(link)
    return render(request, 'schedule_details.html', {"data": data})


def schedule_details(link):
    session = requests.Session()
    content = session.get(link, verify=False).content
    soup = BeautifulSoup(content, "html.parser")
    a = soup.findAll("div", {"class": ["divleft"]})
    schedule_match = []
    schedule_match_head = []
    lis =[]
    for i in a:
        b = i.findAll("ul")
        for re in b:
            li = re.findAll("li")
            lis.append(li)
        schedule_match.append(b)
        head = i.findAll("h2")
        schedule_match_head.append(head)
    final_head = []
    for i in schedule_match_head:
        for re in i:
            title = re.text
            final_head.append(title)

    final =[]
    for i in lis:
        lisf = []
        for re in i:
            dicti = {}
            game = re.find("a")
            dicti['match'] = re.string
            dicti['match_link'] = (game["href"])
            lisf.append(dicti)
        final.append(lisf)

    data = {"final": final, "final_head": final_head}
    return data


def match_details(request):
    link = request.POST.get("link")
    link_org = "https://www.espncricinfo.com"+link

    print(link_org)
    data = matches(link_org)
    return render(request,"matches.html", {"data": data})


def matches(link):
    session = requests.Session()
    content = session.get(link, verify=False).content
    soup = BeautifulSoup(content, "html.parser")
    contents = soup.find("div", {"class": ["content"]})
    results_list = []
    fixtures_list = []
    if contents:

        fixtures = contents.find("div", {"id": ["fixtures"]})

        if fixtures:
            score_list = fixtures.find("ul", {"class": ["score-list"]})
            li = score_list.findAll("li")
            for i in li:
                team = {}
                s = i.find("span", {"class": ["cscore_time time"]})
                if s:
                    team['span'] = i.find("span", {"class":["cscore_time time"]}).text
                    date = i.find("span", {"class": ["cscore_date"]})
                    if date:
                        team['date'] = i.find("span", {"class":["cscore_date"]}).text
                    overview =i.find("div", {"class": ["cscore_info-overview"]})
                    if overview:
                        team['overview'] = i.find("div", {"class": ["cscore_info-overview"]}).text
                    team_first = i.find("li", {"class": ["cscore_item cscore_item--home"]})
                    if team_first:
                        image_first = team_first.find("img", {"class": "cscore_image"})
                        if image_first:
                            team['image_first'] = (image_first['data-src'])
                        team['team_first'] = team_first.find("span", {"class": ["cscore_name cscore_name--short"]}).text
                    team_second = i.find("li", {"class": ["cscore_item cscore_item--away"]})
                    if team_second:
                        image_second = team_second.find("img", {"class": "cscore_image"})
                        if image_second:
                            team['image_second'] = (image_second['data-src'])
                        team['team_second'] = team_second.find("span", {"class": ["cscore_name cscore_name--short"]}).text
                    fixtures_list.append(team)

        results = contents.find("div", {"id": ["results"]})

        if results:
            score_list = results.find("ul", {"class": ["score-list"]})
            li = score_list.findAll("li")
            for i in li:
                team = {}
                s = i.find("span", {"class": ["cscore_time time"]})
                if s:
                    team['span'] = i.find("span", {"class": ["cscore_time time"]}).text
                    date = i.find("span", {"class": ["cscore_date"]})
                    if date:
                        team['date'] = i.find("span", {"class": ["cscore_date"]}).text
                    overview = i.find("div", {"class": ["cscore_info-overview"]})
                    if overview:
                        team['overview'] = i.find("div", {"class": ["cscore_info-overview"]}).text

                    team_first = i.find("li", {"class": ["cscore_item cscore_item--home"]})
                    if team_first:
                        image_first = team_first.find("img", {"class": "cscore_image"})
                        if image_first:
                            team['image_first'] = (image_first['data-src'])
                        team['team_first'] = team_first.find("span", {"class": ["cscore_name cscore_name--short"]}).text
                        cscore_score = team_first.find("div", {"class": ["cscore_score"]})
                        if cscore_score:
                            team['score_first'] = team_first.find("div", {"class": ["cscore_score"]}).text
                    team_second = i.find("li", {"class": ["cscore_item cscore_item--away"]})
                    if team_second:
                        image_second = team_second.find("img", {"class": "cscore_image"})
                        if image_second:
                            team['image_second'] = (image_second['data-src'])
                        team['team_second'] = team_second.find("span", {"class": ["cscore_name cscore_name--short"]}).text
                        cscore_score = team_second.find("div", {"class": ["cscore_score"]})
                        if cscore_score:
                            team['score_second'] = team_second.find("div", {"class": ["cscore_score"]}).text
                    results_list.append(team)

    matches_collection = soup.findAll("div", {"class": ["cscore cscore--pregame cricket cscore--watchNotes"]})
    header_top = soup.find("div", {"class": ["scoreCollection__headerTop"]})
    top = ''
    if header_top:
        top = header_top.find("h1").text
    team_matches_list = []
    if matches_collection:
        for i in matches_collection:
            team_matches = {}
            span = i.find("span", {"class": ["cscore_date"]})
            if span:
                team_matches['span'] = i.find("span", {"class": ["cscore_date"]}).text
            overview = i.find("div", {"class":["cscore_info-overview"]})
            if overview:
                team_matches['overview'] = i.find("div", {"class":["cscore_info-overview"]}).text
            team_first = i.find("li", {"class": ["cscore_item cscore_item--home"]})
            if team_first:
                image_first = team_first.find("img", {"class": "cscore_image"})
                if image_first:
                    team_matches['image_first'] = (image_first['data-src'])
                team_matches['team_first'] = team_first.find("span", {"class": ["cscore_name cscore_name--long"]}).text
                cscore_score = team_first.find("div", {"class": ["cscore_score"]})
                if cscore_score:
                    team_matches['score_first'] = team_first.find("div", {"class": ["cscore_score"]}).text
            team_second = i.find("li", {"class": ["cscore_item cscore_item--away"]})
            if team_second:
                image_second = team_second.find("img", {"class": "cscore_image"})
                if image_second:
                    team_matches['image_second'] = (image_second['data-src'])
                team_matches['team_second'] = team_second.find("span", {"class": ["cscore_name cscore_name--long"]}).text
                cscore_score = team_second.find("div", {"class": ["cscore_score"]})
                if cscore_score:
                    team_matches['score_second'] = team_second.find("div", {"class": ["cscore_score"]}).text
            team_matches_list.append(team_matches)

    data = {"fixtures_list": fixtures_list, "results_list": results_list, "team_matches_list": team_matches_list, "top": top}
    return data


def about(request):
    return render(request, 'about.html')


def batting_ranking(request):
    link = "https://www.cricbuzz.com/cricket-stats/icc-rankings/men/batting"
    data = batting_ranking2(link)
    return render(request, 'batting_ranking.html', {"data": data})


def batting_ranking2(link):
    session = requests.Session()
    content = session.get(link, verify=False).content
    soup = BeautifulSoup(content, "html.parser")
    div = soup.findAll("div", {"class":["cb-col cb-col-100 cb-font-14 cb-lst-itm text-center"]})
    details_player = []
    for rec in div:
        player = {}
        position = rec.find("div", {"class": ["cb-col cb-col-16 cb-rank-tbl cb-font-16"]})
        if position:
            player['position'] = rec.find("div", {"class": ["cb-col cb-col-16 cb-rank-tbl cb-font-16"]}).text

        image = rec.find("img", {"class": ["img-responsive cb-rank-plyr-img"]})
        image1 = rec.find("img", {"class": ["img-responsive"]})
        if image:
            player['img'] = (image['src'])
        elif image1:
            player['img'] = (image1['source'])

        rating = rec.find("div", {"class": ["cb-col cb-col-17 cb-rank-tbl pull-right"]})
        if rating:
            player['rating'] = rec.find("div", {"class": ["cb-col cb-col-17 cb-rank-tbl pull-right"]}).text

        player_name = rec.find("a", {"class": ["text-hvr-underline text-bold cb-font-16"]})
        if player_name:
            player['player_name'] = rec.find("a", {"class": ["text-hvr-underline text-bold cb-font-16"]}).text

        team_name = rec.find("div", {"class": ["cb-font-12 text-gray"]})
        if team_name:
            player['team_name'] = rec.find("div", {"class": ["cb-font-12 text-gray"]}).text

        details_player.append(player)
    return details_player


def bowling_ranking(request):
    link = "https://www.cricbuzz.com/cricket-stats/icc-rankings/men/bowling"
    data = bowling_ranking2(link)
    return render(request, 'bowling_ranking.html', {"data": data})


def bowling_ranking2(link):
    session = requests.Session()
    content = session.get(link, verify=False).content
    soup = BeautifulSoup(content, "html.parser")
    div = soup.findAll("div", {"class": ["cb-col cb-col-100 cb-font-14 cb-lst-itm text-center"]})
    details_player = []
    for rec in div:
        player = {}
        position = rec.find("div", {"class": ["cb-col cb-col-16 cb-rank-tbl cb-font-16"]})
        if position:
            player['position'] = rec.find("div", {"class": ["cb-col cb-col-16 cb-rank-tbl cb-font-16"]}).text

        image = rec.find("img", {"class": ["img-responsive cb-rank-plyr-img"]})
        image1 = rec.find("img", {"class": ["img-responsive"]})
        if image:
            player['img'] = (image['src'])
        elif image1:
            player['img'] = (image1['source'])

        rating = rec.find("div", {"class": ["cb-col cb-col-17 cb-rank-tbl pull-right"]})
        if rating:
            player['rating'] = rec.find("div", {"class": ["cb-col cb-col-17 cb-rank-tbl pull-right"]}).text

        player_name = rec.find("a", {"class": ["text-hvr-underline text-bold cb-font-16"]})
        if player_name:
            player['player_name'] = rec.find("a", {"class": ["text-hvr-underline text-bold cb-font-16"]}).text

        team_name = rec.find("div", {"class": ["cb-font-12 text-gray"]})
        if team_name:
            player['team_name'] = rec.find("div", {"class": ["cb-font-12 text-gray"]}).text

        details_player.append(player)
    return details_player


def all_rounder_ranking(request):
    link = "https://www.cricbuzz.com/cricket-stats/icc-rankings/men/all-rounder"
    data = all_rounder_ranking2(link)
    return render(request, 'all_rounder_ranking.html', {"data": data})


def all_rounder_ranking2(link):
    session = requests.Session()
    content = session.get(link, verify=False).content
    soup = BeautifulSoup(content, "html.parser")
    div = soup.findAll("div", {"class": ["cb-col cb-col-100 cb-font-14 cb-lst-itm text-center"]})
    details_player = []
    for rec in div:
        player = {}
        position = rec.find("div", {"class": ["cb-col cb-col-16 cb-rank-tbl cb-font-16"]})
        if position:
            player['position'] = rec.find("div", {"class": ["cb-col cb-col-16 cb-rank-tbl cb-font-16"]}).text

        image = rec.find("img", {"class": ["img-responsive cb-rank-plyr-img"]})
        image1 = rec.find("img", {"class": ["img-responsive"]})
        if image:
            player['img'] = (image['src'])
        elif image1:
            player['img'] = (image1['source'])

        rating = rec.find("div", {"class": ["cb-col cb-col-17 cb-rank-tbl pull-right"]})
        if rating:
            player['rating'] = rec.find("div", {"class": ["cb-col cb-col-17 cb-rank-tbl pull-right"]}).text

        player_name = rec.find("a", {"class": ["text-hvr-underline text-bold cb-font-16"]})
        if player_name:
            player['player_name'] = rec.find("a", {"class": ["text-hvr-underline text-bold cb-font-16"]}).text

        team_name = rec.find("div", {"class": ["cb-font-12 text-gray"]})
        if team_name:
            player['team_name'] = rec.find("div", {"class": ["cb-font-12 text-gray"]}).text

        details_player.append(player)
    return details_player


def team_ranking(request):
    link = "https://www.cricbuzz.com/cricket-stats/icc-rankings/men/teams"
    data = team_ranking2(link)
    return render(request, 'team_ranking.html', {"data": data})


def team_ranking2(link):
    session = requests.Session()
    content = session.get(link, verify=False).content
    soup = BeautifulSoup(content, "html.parser")
    div = soup.findAll("div", {"class": ["cb-col cb-col-100 cb-font-14 cb-brdr-thin-btm text-center"]})
    team_details = []
    for rec in div:
        team = {}
        position = rec.find("div", {"class": ["cb-col cb-col-20 cb-lst-itm-sm"]})
        if position:
            team['position'] = rec.find("div", {"class": ["cb-col cb-col-20 cb-lst-itm-sm"]}).text

        team_name = rec.find("div", {"class": ["cb-col cb-col-50 cb-lst-itm-sm text-left"]})
        if team_name:
            team['team_name'] = rec.find("div", {"class": ["cb-col cb-col-50 cb-lst-itm-sm text-left"]}).text

        rating = rec.find("div", {"class": ["cb-col cb-col-14 cb-lst-itm-sm"]})
        if rating:
            team['rating'] = rec.find("div", {"class": ["cb-col cb-col-14 cb-lst-itm-sm"]}).text

        point = rec.find("div", {"class": ["cb-col cb-col-14 cb-lst-itm-sm"]})
        if point:
            team['point'] = rec.find("div", {"class": ["cb-col cb-col-14 cb-lst-itm-sm"]}).text
        team_details.append(team)

    return team_details
