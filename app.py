import os, requests, streamlit as st, pandas as pd
from datetime import datetime, timezone
st.set_page_config(page_title='Fliff $1 → $50 Scanner', page_icon='🎯', layout='wide')
st.title('🎯 Fliff $1 → $50 Value Scanner')
st.caption('Read-only odds scanner. No bets placed. $50 total payout on $1 requires decimal odds ≥50 (+4900).')
key = os.getenv('PROPLINE_API_KEY') or st.secrets.get('PROPLINE_API_KEY', '')
if not key:
    st.warning('Set PROPLINE_API_KEY in your deployment secrets. Never commit your key to GitHub.')
    st.stop()
BASE='https://api.prop-line.com/v1'
def get(path,params=None):
    r=requests.get(BASE+path,headers={'X-API-Key':key},params=params,timeout=25)
    r.raise_for_status()
    return r.json()
def decimal(price):
    try:
        p=float(price)
        return 1+p/100 if p>0 else 1+100/abs(p)
    except (ValueError,TypeError,ZeroDivisionError):return 0
try:
    sports=get('/sports')
except Exception as e:
    st.error(f'Could not access PropLine API: {type(e).__name__}. Check key, plan, and network.')
    st.stop()
if isinstance(sports,dict): sports=sports.get('sports',sports.get('data',[]))
options={s.get('title',s.get('key',s.get('sport_key','Unknown'))):s.get('key',s.get('sport_key')) for s in sports if isinstance(s,dict)}
if not options:
    st.error('Sports response has an unexpected format. See the provider documentation.')
    st.stop()
selected=st.multiselect('Sports to scan',list(options),default=[x for x in options if any(t in x.lower() for t in ['nfl','nba'])][:2])
max_events=st.slider('Maximum games per sport',1,30,8)
min_payout=st.number_input('Minimum total payout on $1',min_value=2.0,value=50.0,step=5.0)
run=st.button('Scan live odds',type='primary')
if run:
    rows=[]; failures=[]; books=set(); count=0
    for name in selected:
        sport=options[name]
        try:
            events=get(f'/sports/{sport}/events')
            if isinstance(events,dict): events=events.get('events',events.get('data',[]))
            for ev in events[:max_events]:
                eid=ev.get('id')
                try:
                    # No markets filter: inspect whatever event odds the provider exposes.
                    data=get(f'/sports/{sport}/events/{eid}/odds')
                    count+=1
                    for book in data.get('bookmakers',[]):
                        bkey=book.get('key','').lower(); books.add(bkey)
                        if bkey!='fliff': continue
                        for market in book.get('markets',[]):
                            for out in market.get('outcomes',[]):
                                price=out.get('price_american',out.get('price'))
                                mult=decimal(price)
                                if mult>=min_payout:
                                    rows.append({'Sport':name,'Game':f"{ev.get('away_team','')} @ {ev.get('home_team','')}",'Start':ev.get('commence_time',''),'Market':market.get('key',''),'Player / description':out.get('description',''),'Selection':out.get('name',''),'Line':out.get('point',''),'American odds':price,'$1 total payout':round(mult,2),'Break-even %':round(100/mult,3),'Updated':market.get('last_update','')})
                except Exception as e: failures.append(f'{sport} event {eid}: {type(e).__name__}')
        except Exception as e: failures.append(f'{sport}: {type(e).__name__}')
    st.caption(f'Scanned {count} events. Data returned by PropLine, not directly from the Fliff app.')
    if 'fliff' not in books:
        st.error('Fliff was NOT present in the returned sportsbook data. This provider/plan may not support Fliff. Do not interpret other books as Fliff prices.')
    elif not rows: st.info('Fliff appeared, but no available single selection met the payout threshold.')
    else:
        df=pd.DataFrame(rows).sort_values('$1 total payout',ascending=False)
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button('Download CSV',df.to_csv(index=False),'fliff_matches.csv','text/csv')
        st.warning('These are payout matches, NOT verified +EV bets. An independent calibrated probability model is required to rank value reliably.')
    if failures: st.warning(f'{len(failures)} requests failed; results may be incomplete.')
    if books: st.caption('Bookmaker keys observed: '+', '.join(sorted(books)[:40]))
st.divider()
st.subheader('Value model: what comes next')
st.write('Expected ROI = estimated probability × payout multiplier − 1. We do not invent probabilities from odds alone. Cross-book matching, removal of bookmaker margin, and historical calibration must be added before any +EV rankings are credible.')
