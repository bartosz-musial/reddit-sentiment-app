from dotenv import load_dotenv
import streamlit as st
import psycopg2
import os
import plotly.express as px

load_dotenv()

@st.cache_resource
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    return conn

@st.cache_data(ttl=900)
def get_subreddits(_conn):
    with _conn.cursor() as cur:
        cur.execute("SELECT DISTINCT subreddit FROM posts")
        return [row[0] for row in cur.fetchall()]

@st.cache_data(ttl=900)
def get_sentiment_stats(_conn, subreddit):
    with _conn.cursor() as cur:
        query = """
            SELECT
                sentiment,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
            FROM posts
            WHERE subreddit = %s AND sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE')
            GROUP BY sentiment
        """
        cur.execute(query, (subreddit,))

        stats = {
            "POSITIVE": {'percentage': 0, 'count': 0},
            "NEUTRAL": {'percentage': 0, 'count': 0},
            "NEGATIVE": {'percentage': 0, 'count': 0}
        }

        for sentiment, count, percentage in cur.fetchall():
            stats[sentiment] = {
                "percentage": float(percentage),
                "count": count
            }

        return stats

def main():
    st.title("Reddit Sentiment Analysis Dashboard")

    conn = get_db_connection()
    subreddits = get_subreddits(conn)
    selected_subreddit = st.selectbox(
        "Select Subreddit",
        subreddits
    )

    if selected_subreddit:
        stats = get_sentiment_stats(conn, selected_subreddit)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Positive",
                      f"{stats['POSITIVE']['percentage']}%",
                      f"{stats['POSITIVE']['count']} posts")

        with col2:
            st.metric("Neutral",
                      f"{stats['NEUTRAL']['percentage']}%",
                      f"{stats['NEUTRAL']['count']} posts")

        with col3:
            st.metric("Negative",
                      f"{stats['NEGATIVE']['percentage']}%",
                      f"{stats['NEGATIVE']['count']} posts")

        fig = px.pie(
            names=['Positive', 'Neutral', 'Negative'],
            values=[
                stats['POSITIVE']['percentage'],
                stats['NEUTRAL']['percentage'],
                stats['NEGATIVE']['percentage']
            ],
            title=f'Sentiment Distribution in r/{selected_subreddit}',
            color=['Positive', 'Neutral', 'Negative'],
            color_discrete_map={
                'Positive': '#34a853',
                'Neutral': '#9aa0a6',
                'Negative': '#ea4335'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
