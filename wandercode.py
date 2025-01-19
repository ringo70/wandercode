import streamlit as st
import sqlite3
import os
from datetime import datetime

like_btns = {0: "🚩", 1: "👎", 2: "👍", 3: "♥️"}

# Establish SQLite connection
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Create tables if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS interactions (
        post_id INTEGER,
        user_id TEXT,
        action TEXT,
        UNIQUE(post_id, user_id)
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        post_id INTEGER PRIMARY KEY AUTOINCREMENT,
        content_type TEXT,
        content TEXT,
        datetime TEXT,
        lyrics_path TEXT,
        image_path TEXT,
        audio_path TEXT
    )
''')
conn.commit()

# Ensure the directories exist
os.makedirs("posts/pictures", exist_ok=True)
os.makedirs("posts/mp3", exist_ok=True)
os.makedirs("posts/lyrics", exist_ok=True)

def actions_view(post_id, dt):

    col1, col2, col3, col4 = st.columns([0.27, 0.27, 0.27, 0.19], vertical_alignment="bottom")

    with col1:

        # get counts for interactions: love/like/dislike
        c.execute('SELECT action, count(*) FROM interactions WHERE post_id = ? AND action>0 GROUP BY action', (post_id,))
        counts = c.fetchall()
        actions_counts = {1: 0, 2: 0, 3: 0}
        if len(counts)>0:
            for key, value in counts:
                if key in actions_counts:
                    actions_counts[key] = value
        
        # Check for existing interaction
        c.execute('SELECT action FROM interactions WHERE post_id = ? AND user_id = ?', (post_id, st.session_state.user_id))
        result = c.fetchone()
        if not result: result=[0]

        # if st.button(like_btns.get(3) + r'''$\textsf{ \tiny id: '''+ str(actions_counts.get(3)) + '''}$''', key=f'love_{post_id}'):
        if st.button(like_btns.get(3) + " " + str(actions_counts.get(3)), key=f'love_{post_id}'):
            action = 3
            if result[0] == 3: action = 0
            dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute('INSERT OR REPLACE INTO interactions (post_id, user_id, action, dt) VALUES (?, ?, ?, ?)', (post_id, st.session_state.user_id, action, dt))
            conn.commit()
            st.rerun()
        with col2: 
            if st.button(like_btns.get(2) + " " + str(actions_counts.get(2)), key=f'like_{post_id}'):
                action = 2
                if result[0] == 2: action = 0
                dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute('INSERT OR REPLACE INTO interactions (post_id, user_id, action, dt) VALUES (?, ?, ?, ?)', (post_id, st.session_state.user_id, action, dt))
                conn.commit()
                st.rerun()
        with col3:
            if st.button(like_btns.get(1) + " " + str(actions_counts.get(1)), key=f'dislike_{post_id}'):
                action = 1
                if result[0] == 1: action = 0
                dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute('INSERT OR REPLACE INTO interactions (post_id, user_id, action, dt) VALUES (?, ?, ?, ?)', (post_id, st.session_state.user_id, action, dt))
                conn.commit()
                st.rerun()
            
    with col4:
        # output post ID and post datetime in a smaller font on the right bottom side
        label = r'''$\textsf{\tiny id: ''' + str(post_id) + ''' on ''' + str(dt) + '''}$'''
        st.write(label)
    
    return

# Function to display posts
def display_posts():
    
    c.execute('SELECT * FROM posts ORDER BY post_id DESC LIMIT 100')
    posts = c.fetchall()
    for post_id, content_type, content, image_path, audio_path, lyrics_path, dt in posts:
        with st.container(border=True):

            if content_type == "mixed":
                if image_path:
                    # st.image(image_path, caption='Image Post')
                    st.image(image_path, caption='')        
                if content:
                    with st.container(border=True):
                        st.write(content)
                if audio_path:
                    st.audio(audio_path)
                if st.session_state.user_id: actions_view(post_id, dt)
                if lyrics_path:
                    with open(lyrics_path, 'r') as file:
                        lyrics_original = file.read()
                        lyrics_returns_fixed = lyrics_original.replace("\n", "  \n")
                        lyrics_verse_fixed = lyrics_returns_fixed.replace("[Verse", "[verse")
                        lyrics_all_fixed = lyrics_verse_fixed.replace("[Chorus", "[Chorus")
                    st.expander("", expanded=False, icon=None)
                    with st.expander("lyrics"):
                        st.write(lyrics_all_fixed)            
            elif content_type == "image":
                st.image(image_path, caption='Image Post')
                if st.session_state.user_id: actions_view(post_id, dt)
            elif content_type == "story":
                st.write(content)
                if st.session_state.user_id: actions_view(post_id, dt)
            elif content_type == "mp3":
                st.audio(audio_path)
                if lyrics_path:
                    with open(lyrics_path, 'r') as file:
                        lyrics_original = file.read()
                        lyrics_returns_fixed = lyrics_original.replace("\n", "  \n")
                        lyrics_verse_fixed = lyrics_returns_fixed.replace("[Verse", "[verse")
                        lyrics_all_fixed = lyrics_verse_fixed.replace("[Chorus", "[Chorus")
                    st.expander("", expanded=False, icon=None)
                    with st.expander("lyrics"):
                        st.write(lyrics_all_fixed)    
                if st.session_state.user_id: actions_view(post_id, dt)


# Main Streamlit App
st.logo("assets/logo2.png", size="large", link=None, icon_image="assets/logo2.png")
# st.title("WanderCode")

uid = st.experimental_user.to_dict()
st.session_state.user_id = uid.get("email")
# print("st.session_state.user_id: ",type(st.session_state.user_id), st.session_state.user_id)
# st.session_state.user_id = None
# print("_st.session_state.user_id: ",type(st.session_state.user_id), st.session_state.user_id)

display_posts()

# Posting new content
# This is only allowed by me
if st.session_state.user_id == "ringoharms@gmail.com" or st.session_state.user_id == "test@example.com":

    st.sidebar.title("Post New Content")
    story_content = st.sidebar.text_area("Story Content (optional)")
    uploaded_image = st.sidebar.file_uploader("Upload Image (optional)", type=["jpg", "jpeg", "png"])
    uploaded_audio = st.sidebar.file_uploader("Upload MP3 (optional)", type=["mp3"])
    uploaded_lyrics = st.sidebar.file_uploader("Upload lyrics (optional)", type=["txt"])

    if st.sidebar.button("Post"):
        content_type = 'mixed' if uploaded_image or uploaded_audio or story_content or uploaded_lyrics else None
        image_path, audio_path, lyrics_path = None, None, None

        if uploaded_image:
            image_path = f"posts/pictures/{uploaded_image.name}"
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

        if uploaded_audio:
            audio_path = f"posts/mp3/{uploaded_audio.name}"
            with open(audio_path, "wb") as f:
                f.write(uploaded_audio.getbuffer())

        if uploaded_lyrics:
            lyrics_path = f"posts/lyrics/{uploaded_lyrics.name}"
            with open(lyrics_path, "wb") as f:
                f.write(uploaded_lyrics.getbuffer())

        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute('INSERT INTO posts (content_type, content, image_path, audio_path, lyrics_path, dt) VALUES (?, ?, ?, ?, ?, ?)', 
                (content_type, story_content, image_path, audio_path, lyrics_path, dt))
        
        # get thepost_id from the new post 
        post_id = c.lastrowid

        # create a record in the interactions table in order to have at least one record for the total counts of likes
        c.execute('INSERT INTO interactions (post_id, user_id, action, dt) VALUES (?, ?, ?, ?)', 
                (post_id, "ringoharms@gmail.com", 2, dt))

        conn.commit()
        st.success("Post created successfully!")
        story_content = ""
        uploaded_image = ""
        uploaded_audio = ""
        uploaded_lyrics = ""
        st.rerun()

    # Close the connection when done
    conn.close()