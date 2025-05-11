import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import numpy as np

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'connections' not in st.session_state:
    st.session_state.connections = []
if 'messages' not in st.session_state:
    st.session_state.messages = {}

# Page Config with DataLink-like theme
st.set_page_config(
    page_title="DataLink Clone",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)
##########################
### DataLink CSS
##########################

st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --linkedin-blue: #0a66c2;
        --linkedin-light-blue: #70b5f9;
        --linkedin-dark-blue: #004182;
        --linkedin-gray: #eef3f8;
        --linkedin-dark-gray: #666666;
        --linkedin-light-gray: #f3f2ef;
    }

    /* Background styling */
    .login-background {
        background-image: url('https://static.licdn.com/sc/h/55k1z8997gh8dwtihm11aajyq');
        background-size: cover;
        background-position: center;
        height: 100vh;
    display: flex;
        justify-content: center;
    align-items: center;
    }

    .login-container {
        background: white;
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        width: 400px;
    }

    /* Navigation styling */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 32px;
        background: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.07);
        position: sticky;
        top: 0;
        z-index: 999;
        min-height: 64px;
        margin-bottom: 8px;
    }

    .nav-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .nav-search {
        padding: 10px 16px;
        width: 320px;
        border: 1px solid #ccc;
        border-radius: 6px;
        background-color: #eef3f8;
        font-size: 16px;
    }

    .nav-center {
        display: flex;
        gap: 32px;
    }

    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: var(--linkedin-dark-gray);
        font-size: 13px;
        cursor: pointer;
        padding: 6px 10px;
        text-decoration: none;
        min-width: 60px;
        transition: color 0.2s;
    }

    .nav-item:hover {
        color: var(--linkedin-blue);
    }

    .nav-right {
        display: flex;
        gap: 12px;
        align-items: center;
    }

    /* Right sidebar styling */
    .sidebar-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        margin-bottom: 16px;
        padding: 16px;
    }

    .sidebar-title {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        color: var(--linkedin-dark-gray);
    }

    .sidebar-item {
        display: flex;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #e0e0e0;
    }

    .sidebar-item:last-child {
        border-bottom: none;
    }

    .sidebar-item img {
        width: 48px;
        height: 48px;
        border-radius: 4px;
        margin-right: 12px;
    }

    .sidebar-item-content {
        flex: 1;
    }

    .sidebar-item-title {
        font-weight: 600;
    font-size: 14px;
}

    .sidebar-item-subtitle {
        color: var(--linkedin-dark-gray);
        font-size: 12px;
    }

    .sidebar-button {
        background: transparent;
        border: 1px solid var(--linkedin-blue);
        color: var(--linkedin-blue);
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 12px;
        cursor: pointer;
    }

    .sidebar-button:hover {
        background: #eef3f8;
}

    .notification-badge {
        background-color: var(--linkedin-blue);
        color: white;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 50%;
        position: absolute;
        top: 0px;
        right: -10px;
    }
</style>
""", unsafe_allow_html=True)

# Logo path
LOGO_PATH = "DataLink_LOGO.png"

# Login and Signup tabs
def login_signup_tabs():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_PATH, width=50, use_container_width=True)
        st.markdown("<h2 style='text-align: center;'>Welcome to DataLink</h2>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Signup"])

        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login"):
                try:
                    response = requests.post("http://localhost:8000/api/auth/login", json={
                        "email": email,
                        "password": password
                    })
                    if response.status_code == 200:
                        user = response.json()
                        st.session_state.authenticated = True
                        st.session_state.current_user = user
                        st.success("✅ Login successful")
                        st.rerun()
                    else:
                        st.error(response.json()["detail"])
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        with tab2:
            full_name = st.text_input("Full Name", key="signup_fullname")
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            role = st.text_input("Professional Role", key="signup_role")
            company = st.text_input("Company", key="signup_company")
            location = st.text_input("Location", key="signup_location")
            about = st.text_area("About You", key="signup_about")

            # --- Skills ---
            st.markdown("### Skills")
            if "skills_list" not in st.session_state:
                st.session_state.skills_list = []
            if "skill_to_delete" not in st.session_state:
                st.session_state.skill_to_delete = None

            with st.form("add_skill_form", clear_on_submit=True):
                new_skill = st.text_input("Enter a skill")
                add_skill = st.form_submit_button("➕ Add Skill")

            if add_skill and new_skill and new_skill not in st.session_state.skills_list:
                st.session_state.skills_list.append(new_skill)

            for i, skill in enumerate(st.session_state.skills_list):
                col1, col2 = st.columns([6, 1])
                with col1:
                    st.markdown(f"- {skill}")
                with col2:
                    if st.button("❌", key=f"delete_skill_{i}"):
                        st.session_state.skill_to_delete = i
            if st.session_state.skill_to_delete is not None:
                del st.session_state.skills_list[st.session_state.skill_to_delete]
                st.session_state.skill_to_delete = None

            # --- Experience ---
            st.markdown("### Experience")
            if "experience_entries" not in st.session_state:
                st.session_state.experience_entries = []
            with st.form("add_exp_form", clear_on_submit=True):
                exp_title = st.text_input("Job Title")
                exp_company = st.text_input("Company")
                exp_duration = st.text_input("Duration (e.g., 2020 - Present)")
                exp_desc = st.text_area("Job Description")
                add_exp = st.form_submit_button("➕ Add Experience")
            if add_exp and exp_title:
                st.session_state.experience_entries.append({
                    "title": exp_title,
                    "company": exp_company,
                    "duration": exp_duration,
                    "description": exp_desc
                })
            for i, exp in enumerate(st.session_state.experience_entries):
                st.markdown(f"🧑‍💼 **{exp['title']}**, {exp['company']} ({exp['duration']})\n- {exp['description']}")

            # --- Education ---
            st.markdown("### Education")
            if "education_entries" not in st.session_state:
                st.session_state.education_entries = []
            with st.form("add_edu_form", clear_on_submit=True):
                edu_school = st.text_input("School")
                edu_degree = st.text_input("Degree")
                edu_duration = st.text_input("Duration (e.g., 2016 - 2018)")
                add_edu = st.form_submit_button("➕ Add Education")
            if add_edu and edu_school:
                st.session_state.education_entries.append({
                    "school": edu_school,
                    "degree": edu_degree,
                    "duration": edu_duration
                })
            for edu in st.session_state.education_entries:
                st.markdown(f"🎓 **{edu['degree']}** - {edu['school']} ({edu['duration']})")

            # --- Submit Button ---
            if st.button("Sign Up"):
                payload = {
                    "full_name": full_name,
                    "email": signup_email,
                    "password": signup_password,
                    "role": role,
                    "company": company,
                    "location": location,
                    "about": about,
                    "skills": st.session_state.skills_list,
                    "experience": st.session_state.experience_entries,
                    "education": st.session_state.education_entries
                }

                try:
                    response = requests.post("http://localhost:8000/api/auth/signup", json=payload)
                    if response.status_code == 200:
                        st.success("🎉 Signup successful! Please login now.")
                        st.session_state.skills_list.clear()
                        st.session_state.experience_entries.clear()
                        st.session_state.education_entries.clear()
                    else:
                        st.error(response.json().get("detail", "Signup failed."))
                except Exception as e:
                    st.error(f"❌ Error: {e}")

##########################
### Rendering -> Header, Sidebar, and Home Feed
##########################

# --- Header Navigation ---
def render_header():
    if not st.session_state.authenticated:
        login_signup_tabs()
        return False

    left_col, center_col, right_col = st.columns([2, 6, 1.5])
    
    with left_col:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(LOGO_PATH, width=80) 
        with col2:
            st.text_input("Search", label_visibility="collapsed")
    
    with center_col:
        nav_cols = st.columns(5)
        
        st.markdown("""
        <style>
        .nav-button {
            text-align: center;
            padding: 5px;
        }
        .nav-icon {
            font-size: 22px;
            display: block;
        }
        .nav-text {
            font-size: 14px;
            margin-top: 4px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        nav_items = [
            ("🏠", "Home Feed"),
            ("👥", "Connections"),
            ("💼", "Job Board"),
            ("💬", "Messaging"),
            ("🔔", "Notifications")
        ]

        # Initialize the current page
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Home Feed"

        for i, (icon, text) in enumerate(nav_items):
            with nav_cols[i]:
                if st.button(f"{icon}", key=f"nav_{text}"):
                    st.session_state.current_page = text

                is_active = st.session_state.current_page == text
                label_style = "font-weight:bold;" if is_active else ""
                st.markdown(f"<div class='nav-text' style='{label_style}'>{text}</div>", unsafe_allow_html=True)


    
    with right_col:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image("https://randomuser.me/api/portraits/men/32.jpg", width=45)
        with col2:
            st.button("Me ▼", use_container_width=True)
    
    return True

# --- Sidebar Navigation ---
def render_sidebar():
    if not st.session_state.authenticated:
        return
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", [
        "Home Feed", 
        "Profile", 
        "Job Board", 
        "Connections", 
        "Messaging",
        "Notifications",
        "Analytics",
        "Settings"
    ])
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Actions")
    if st.sidebar.button("📝 Create Post"):
        st.session_state.show_post_creator = True
    if st.sidebar.button("🔍 Search Jobs"):
        st.session_state.show_job_search = True
    if st.sidebar.button("👥 Find Connections"):
        st.session_state.show_connection_finder = True
    return page

# --- Home Feed Page ---
def render_home_feed():
    st.title("🏠 Home")
    left_col, center_col, right_col = st.columns([2, 5, 2])
    with left_col:
        render_profile_card()
    with center_col:
        if st.session_state.get('show_post_creator', False):
            with st.form("post_creator"):
                post_content = st.text_area("What's on your mind?", height=100)
                post_type = st.radio("Post Type", ["Text", "Image", "Article"])
                if post_type == "Image":
                    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])
                if post_type == "Article":
                    article_link = st.text_input("Article URL")
                submit = st.form_submit_button("Post")
                if submit:
                    st.success("Post created successfully!")
                    st.session_state.show_post_creator = False
        st.markdown("---")
        posts = [
            {
                "name": "Sarah Johnson",
                "role": "Product Manager at Microsoft",
                "profile_pic": "https://randomuser.me/api/portraits/women/44.jpg",
                "content": "Excited to share that our team just launched a new AI-powered feature for Microsoft Teams! 🚀 #AI #ProductManagement #Microsoft",
                "image": "https://images.unsplash.com/photo-1551434678-e076c223a692?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80",
                "timestamp": "2h ago",
                "likes": 143,
                "comments": [
                    {"name": "John", "pic": "https://randomuser.me/api/portraits/men/12.jpg", "text": "Great work! Looking forward to trying it out.", "timestamp": "1h ago"},
                    {"name": "Sarah", "pic": "https://randomuser.me/api/portraits/women/22.jpg", "text": "The AI integration looks promising!", "timestamp": "30m ago"},
                    {"name": "Alex", "pic": "https://randomuser.me/api/portraits/men/23.jpg", "text": "Congrats to the team!", "timestamp": "10m ago"}
                ],
                "shares": 15,
                "type": "image"
            },
            {
                "name": "Michael Chen",
                "role": "Data Scientist at Netflix",
                "profile_pic": "https://randomuser.me/api/portraits/men/45.jpg",
                "content": "Just published a new research paper on recommendation systems. Check it out!",
                "timestamp": "5h ago",
                "likes": 58,
                "comments": [
                    {"name": "Emily", "pic": "https://randomuser.me/api/portraits/women/33.jpg", "text": "Awesome work!", "timestamp": "4h ago"}
                ],
                "shares": 12,
                "type": "article",
                "article_link": "https://arxiv.org/abs/2301.12345",
                "article_title": "Advanced Recommendation Systems: A Deep Learning Approach",
                "article_image": "https://images.unsplash.com/photo-1551288049-ebf251d575d3?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80"
            },
            {
                "name": "Emily Rodriguez",
                "role": "UX Designer at Apple",
                "profile_pic": "https://randomuser.me/api/portraits/women/46.jpg",
                "content": "Sharing my latest design work for the new iOS update. What do you think? #Design #UX #Apple",
                "image": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80",
                "timestamp": "1d ago",
                "likes": 189,
                "comments": [
                    {"name": "Alex", "pic": "https://randomuser.me/api/portraits/men/23.jpg", "text": "Love the new interface!", "timestamp": "20h ago"},
                    {"name": "Sarah", "pic": "https://randomuser.me/api/portraits/women/22.jpg", "text": "The animations are smooth!", "timestamp": "18h ago"},
                    {"name": "John", "pic": "https://randomuser.me/api/portraits/men/12.jpg", "text": "Looks great!", "timestamp": "15h ago"}
                ],
                "shares": 25,
                "type": "image"
            },
            # 7 more dummy posts
            {
                "name": "Ava Smith",
                "role": "Marketing Lead at Shopify",
                "profile_pic": "https://randomuser.me/api/portraits/women/50.jpg",
                "content": "Our new campaign just went live! Check out the creative visuals.",
                "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
                "timestamp": "3h ago",
                "likes": 77,
                "comments": [
                    {"name": "Ben", "pic": "https://randomuser.me/api/portraits/men/51.jpg", "text": "Love the colors!", "timestamp": "2h ago"}
                ],
                "shares": 8,
                "type": "image"
            },
            {
                "name": "Liam Turner",
                "role": "DevOps Engineer at Atlassian",
                "profile_pic": "https://randomuser.me/api/portraits/men/52.jpg",
                "content": "Automated our CI/CD pipeline for faster deployments 🚀",
                "image": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=800&q=80",
                "timestamp": "6h ago",
                "likes": 101,
                "comments": [
                    {"name": "Nina", "pic": "https://randomuser.me/api/portraits/women/53.jpg", "text": "Impressive!", "timestamp": "5h ago"}
                ],
                "shares": 10,
                "type": "image"
            },
            {
                "name": "Sophia Lee",
                "role": "HR Manager at Google",
                "profile_pic": "https://randomuser.me/api/portraits/women/54.jpg",
                "content": "We're hiring! Join our amazing team at Google.",
                "image": "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=800&q=80",
                "timestamp": "8h ago",
                "likes": 210,
                "comments": [
                    {"name": "Tom", "pic": "https://randomuser.me/api/portraits/men/55.jpg", "text": "Just applied!", "timestamp": "7h ago"}
                ],
                "shares": 30,
                "type": "image"
            },
            {
                "name": "Noah Brown",
                "role": "CTO at FinTechX",
                "profile_pic": "https://randomuser.me/api/portraits/men/56.jpg",
                "content": "Proud to announce our Series B funding round!",
                "image": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?auto=format&fit=crop&w=800&q=80",
                "timestamp": "10h ago",
                "likes": 320,
                "comments": [
                    {"name": "Emma", "pic": "https://randomuser.me/api/portraits/women/57.jpg", "text": "Congrats!", "timestamp": "9h ago"}
                ],
                "shares": 50,
                "type": "image"
            },
            {
                "name": "Olivia Green",
                "role": "Content Writer at Medium",
                "profile_pic": "https://randomuser.me/api/portraits/women/58.jpg",
                "content": "Published a new article on productivity hacks!",
                "timestamp": "12h ago",
                "likes": 88,
                "comments": [
                    {"name": "Lucas", "pic": "https://randomuser.me/api/portraits/men/59.jpg", "text": "Great read!", "timestamp": "11h ago"}
                ],
                "shares": 12,
                "type": "article",
                "article_link": "https://medium.com/@olivia/productivity-hacks-2023-123456",
                "article_title": "Productivity Hacks for 2023",
                "article_image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80"
            },
            {
                "name": "William Scott",
                "role": "Full Stack Developer at Facebook",
                "profile_pic": "https://randomuser.me/api/portraits/men/60.jpg",
                "content": "Just finished a big React project!",
                "image": "https://images.unsplash.com/photo-1465101178521-c1a9136a3b99?auto=format&fit=crop&w=800&q=80",
                "timestamp": "14h ago",
                "likes": 67,
                "comments": [
                    {"name": "Sophia", "pic": "https://randomuser.me/api/portraits/women/61.jpg", "text": "Congrats!", "timestamp": "13h ago"}
                ],
                "shares": 7,
                "type": "image"
            },
            {
                "name": "Mia White",
                "role": "Data Analyst at IBM",
                "profile_pic": "https://randomuser.me/api/portraits/women/62.jpg",
                "content": "Data visualization is key to insights!",
                "image": "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?auto=format&fit=crop&w=800&q=80",
                "timestamp": "16h ago",
                "likes": 54,
                "comments": [
                    {"name": "Liam", "pic": "https://randomuser.me/api/portraits/men/63.jpg", "text": "Absolutely!", "timestamp": "15h ago"}
                ],
                "shares": 6,
                "type": "image"
            },
            {
                "name": "James King",
                "role": "AI Researcher at OpenAI",
                "profile_pic": "https://randomuser.me/api/portraits/men/64.jpg",
                "content": "Working on GPT-4 improvements!",
                "image": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=800&q=80",
                "timestamp": "18h ago",
                "likes": 400,
                "comments": [
                    {"name": "Olivia", "pic": "https://randomuser.me/api/portraits/women/65.jpg", "text": "Can't wait!", "timestamp": "17h ago"}
                ],
                "shares": 80,
                "type": "image"
            }
        ]
        for i, post in enumerate(posts):
            st.markdown(f"""
            <div class="post" style="background: white; border-radius: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.07); margin-bottom: 24px; padding: 18px;">
                <div class="post-header" style="display: flex; align-items: center; margin-bottom: 10px;">
                    <img class="post-author-pic" src="{post['profile_pic']}" style="width: 48px; height: 48px; border-radius: 50%; margin-right: 12px;">
                    <div>
                        <div class="post-author-name" style="font-weight: 600; font-size: 15px;">{post['name']}</div>
                        <div class="post-time" style="color: #666; font-size: 12px;">{post['role']} • {post['timestamp']}</div>
                    </div>
                </div>
                <div class="post-content" style="margin-bottom: 10px; font-size: 15px;">{post['content']}</div>
                {f'<img src="{post["image"]}" style="width:100%; max-width:480px; border-radius:8px; margin-bottom:10px;">' if post.get('image') else ''}
                {f'<a href="{post["article_link"]}" target="_blank"><img src="{post["article_image"]}" style="width:100%; max-width:480px; border-radius:8px; margin-bottom:10px;"><div style="font-weight:600;">{post["article_title"]}</div></a>' if post.get('type') == 'article' else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Use Streamlit native buttons for post actions
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"👍 Like ({post['likes']})", key=f"like_{i}"):
                    post['likes'] += 1
            with col2:
                st.button(f"💬 Comment ({len(post['comments'])})", key=f"comment_{i}")
            with col3:
                st.button(f"🔗 Share ({post['shares']})", key=f"share_{i}")
            
            if post['comments']:
                with st.expander("View Comments"):
                    for comment in post['comments']:
                        st.markdown(f"""
                        <div style="display:flex; align-items:center; margin: 8px 0; padding: 8px; background: #f3f2ef; border-radius: 4px;">
                            <img src="{comment['pic']}" style="width:32px; height:32px; border-radius:50%; margin-right:8px;">
                            <div>
                                <div style="font-weight: 600;">{comment['name']}</div>
                                <div style="color: #666666; font-size: 12px;">{comment['timestamp']}</div>
                                <div>{comment['text']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            st.markdown("---")
    with right_col:
        render_suggestions()

# --- Profile Page ---
def render_profile():
    st.title("👤 Profile Page")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(LOGO_PATH, width=120)
    with col2:
        st.subheader(st.session_state.current_user["name"])
        st.write(st.session_state.current_user["role"])

        if "show_profile_form" not in st.session_state:
            st.session_state.show_profile_form = False
        if "profile_saved" not in st.session_state:
            st.session_state.profile_saved = False

        if st.button("✏️ Edit Profile"):
            st.session_state.show_profile_form = True
            st.session_state.profile_saved = False

        if st.session_state.show_profile_form and not st.session_state.profile_saved:
            with st.form("profile_form"):
                new_name = st.text_input("Full Name", value=st.session_state.current_user["name"])
                new_role = st.text_input("Role", value=st.session_state.current_user["role"])
                submitted = st.form_submit_button("Save")

                if submitted:
                    st.session_state.current_user["name"] = new_name
                    st.session_state.current_user["role"] = new_role
                    st.session_state.profile_saved = True

                    update_data = st.session_state.current_user.copy()
                    update_data.pop("user_id", None)
                    user_id = st.session_state.current_user["user_id"]

                    response = requests.put(
                        f"http://localhost:8000/api/user_profiles/{user_id}",
                        json=update_data
                    )

                    if response.status_code == 200:
                        st.success("✅ Profile updated!")
                    else:
                        st.error("❌ Failed to update profile.")

        if st.session_state.profile_saved:
            st.session_state.show_profile_form = False

    
    # Profile Sections
    tab1, tab2, tab3, tab4 = st.tabs(["About", "Experience", "Education", "Skills"])
    
    with tab1:
        st.subheader("About")
        st.write(st.session_state.current_user["about"])

        # Toggle form visibility
        if "show_about_form" not in st.session_state:
            st.session_state.show_about_form = False
        if "about_saved" not in st.session_state:
            st.session_state.about_saved = False

        if st.button("✏️ Edit About"):
            st.session_state.show_about_form = True
            st.session_state.about_saved = False  # reset saved state

        # Only show form if not already saved
        if st.session_state.show_about_form and not st.session_state.about_saved:
            with st.form("about_form"):
                new_about = st.text_area("Edit your About section", value=st.session_state.current_user["about"])
                submitted = st.form_submit_button("Save")

                if submitted:
                    st.session_state.current_user["about"] = new_about
                    st.session_state.about_saved = True  # mark as saved

                    update_data = st.session_state.current_user.copy()
                    update_data.pop("user_id", None)
                    user_id = st.session_state.current_user["user_id"]

                    response = requests.put(
                        f"http://localhost:8000/api/user_profiles/{user_id}",
                        json=update_data
                    )

                    if response.status_code == 200:
                        st.success("✅ About section updated!")
                    else:
                        st.error("❌ Failed to update profile.")

        # Hide form after saved
        if st.session_state.about_saved:
            st.session_state.show_about_form = False



    
    with tab2:
        st.subheader("Experience")

        if "show_experience_form" not in st.session_state:
            st.session_state.show_experience_form = False
        if "experience_saved" not in st.session_state:
            st.session_state.experience_saved = False

        for exp in st.session_state.current_user.get("experience", []):
            st.write(f"**{exp['title']}**")
            st.write(f"{exp['company']} - {exp['duration']}")
            st.write(exp["description"])

        if st.button("Add Experience", key="add_experience"):
            st.session_state.show_experience_form = True
            st.session_state.experience_saved = False

        if st.session_state.show_experience_form and not st.session_state.experience_saved:
            with st.form("experience_form"):
                new_title = st.text_input("Job Title")
                new_company = st.text_input("Company")
                new_duration = st.text_input("Duration")
                new_desc = st.text_area("Description")
                submitted = st.form_submit_button("Save")

                if submitted:
                    new_exp = {
                        "title": new_title,
                        "company": new_company,
                        "duration": new_duration,
                        "description": new_desc
                    }
                    st.session_state.current_user["experience"].append(new_exp)
                    st.session_state.experience_saved = True

                    update_data = st.session_state.current_user.copy()
                    update_data.pop("user_id", None)
                    user_id = st.session_state.current_user["user_id"]

                    response = requests.put(
                        f"http://localhost:8000/api/user_profiles/{user_id}",
                        json=update_data
                    )

                    if response.status_code == 200:
                        st.success("✅ Experience added!")
                    else:
                        st.error("❌ Failed to update profile.")

        if st.session_state.experience_saved:
            st.session_state.show_experience_form = False

    
    with tab3:
        st.subheader("Education")

        if "show_education_form" not in st.session_state:
            st.session_state.show_education_form = False
        if "education_saved" not in st.session_state:
            st.session_state.education_saved = False

        for edu in st.session_state.current_user.get("education", []):
            st.write(f"**{edu['school']}**")
            st.write(f"{edu['degree']}, {edu['duration']}")

        if st.button("Add Education", key="add_education"):
            st.session_state.show_education_form = True
            st.session_state.education_saved = False

        if st.session_state.show_education_form and not st.session_state.education_saved:
            with st.form("education_form"):
                new_school = st.text_input("School")
                new_degree = st.text_input("Degree")
                new_duration = st.text_input("Duration (e.g., 2016 - 2020)")
                submitted = st.form_submit_button("Save")

                if submitted:
                    new_edu = {
                        "school": new_school,
                        "degree": new_degree,
                        "duration": new_duration
                    }
                    st.session_state.current_user["education"].append(new_edu)
                    st.session_state.education_saved = True

                    update_data = st.session_state.current_user.copy()
                    update_data.pop("user_id", None)
                    user_id = st.session_state.current_user["user_id"]

                    response = requests.put(
                        f"http://localhost:8000/api/user_profiles/{user_id}",
                        json=update_data
                    )

                    if response.status_code == 200:
                        st.success("✅ Education added!")
                    else:
                        st.error("❌ Failed to update profile.")

        if st.session_state.education_saved:
            st.session_state.show_education_form = False

    
    with tab4:
        st.subheader("Skills")

        if "show_skills_form" not in st.session_state:
            st.session_state.show_skills_form = False
        if "skills_saved" not in st.session_state:
            st.session_state.skills_saved = False

        for skill in st.session_state.current_user.get("skills", []):
            st.write(f"**{skill}**")

        if st.button("Add Skills", key="add_skills"):
            st.session_state.show_skills_form = True
            st.session_state.skills_saved = False

        if st.session_state.show_skills_form and not st.session_state.skills_saved:
            with st.form("skills_form"):
                new_skill = st.text_input("Enter a new skill")
                submitted = st.form_submit_button("Save")

                if submitted and new_skill.strip():
                    st.session_state.current_user["skills"].append(new_skill.strip())
                    st.session_state.skills_saved = True

                    update_data = st.session_state.current_user.copy()
                    update_data.pop("user_id", None)
                    user_id = st.session_state.current_user["user_id"]

                    response = requests.put(
                        f"http://localhost:8000/api/user_profiles/{user_id}",
                        json=update_data
                    )

                    if response.status_code == 200:
                        st.success("✅ Skill added!")
                    else:
                        st.error("❌ Failed to update profile.")

        if st.session_state.skills_saved:
            st.session_state.show_skills_form = False

    
    # Activity Section
    st.markdown("---")
    st.subheader("Activity")
    st.write("Your recent activity will appear here")

# --- Job Board Page ---
def render_job_board():
    st.title("💼 Jobs")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        search_query = st.text_input("Search jobs")
    with col2:
        location = st.selectbox("Location", ["All", "Remote", "On-site", "Hybrid"])
    with col3:
        job_type = st.selectbox("Job Type", ["All", "Full-time", "Part-time", "Contract"])
    
    # Job Listings
    for job in JOB_LISTINGS:
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h3 style="margin: 0; color: var(--linkedin-blue);">{job['title']}</h3>
                    <div style="color: var(--linkedin-dark-gray);">{job['company']} • {job['location']}</div>
                    <div style="color: var(--linkedin-dark-gray); font-size: 12px;">Posted {job['posted']} • {job['applicants']}</div>
                </div>
                <div>
                    <button style="background: var(--linkedin-blue); color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">Apply</button>
                </div>
            </div>
            <div style="margin: 16px 0;">
                {job['description']}
            </div>
            <div style="display: flex; gap: 8px; margin-bottom: 16px;">
                <div style="background: #eef3f8; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{job['job_type']}</div>
                <div style="background: #eef3f8; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{job['remote']}</div>
                <div style="background: #eef3f8; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{job['salary']}</div>
            </div>
            <div style="color: var(--linkedin-dark-gray); font-size: 12px;">
                {job['company_info']['size']} • {job['company_info']['industry']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Connections Page ---
def render_connections():
    st.title("🤝 Connections")
    
    # Search and filter connections
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("Search connections")
    with col2:
        filter_by = st.selectbox("Filter by", ["All", "Recent", "Location", "Industry"])
    
    # Connection list
    st.subheader("Your Connections")
    for conn in CONNECTIONS:
        if search.lower() in conn["name"].lower():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=50)
            with col2:
                st.write(f"**{conn['name']}**")
                st.write(f"{conn['role']} at {conn['company']}")
                if st.button("Message", key=f"msg_{conn['name']}"):
                    st.session_state.selected_chat = conn["name"]
                    st.rerun()
            st.markdown("---")
    
    # Connection suggestions
    st.subheader("People you may know")
    suggestions = [
        {"name": "Alex Brown", "role": "Product Designer", "company": "Design Co"},
        {"name": "Sarah Wilson", "role": "Marketing Manager", "company": "Marketing Pro"}
    ]
    
    for person in suggestions:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=50)
        with col2:
            st.write(f"**{person['name']}**")
            st.write(f"{person['role']} at {person['company']}")
        with col3:
            if st.button("Connect", key=f"conn_{person['name']}"):
                st.success(f"Connection request sent to {person['name']}")
# --- Messaging Page ---
def render_messaging():
    st.title("💬 Messaging")
    
    # Layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Conversations")
        search = st.text_input("Search conversations")
        
        # Conversation list
        conversations = [
            {
                "name": "Sarah Johnson",
                "last_message": "Let's meet tomorrow to discuss the project",
                "time": "2h ago",
                "unread": True,
                "role": "Product Manager at Microsoft"
            },
            {
                "name": "LinkedIn Team",
                "last_message": "Welcome to LinkedIn! Here are some tips to get started...",
                "time": "1d ago",
                "unread": False,
                "role": "LinkedIn"
            },
            {
                "name": "Michael Chen",
                "last_message": "Thanks for sharing the article!",
                "time": "3d ago",
                "unread": False,
                "role": "Data Scientist at Netflix"
            }
        ]
        
        for conv in conversations:
            if search.lower() in conv["name"].lower():
                st.markdown(f"""
                <div style="display: flex; align-items: center; padding: 8px; border-radius: 4px; cursor: pointer; hover: background: #f3f2ef;">
                    <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 8px;">
                    <div>
                        <div style="font-weight: 600;">{conv['name']}</div>
                        <div style="color: var(--linkedin-dark-gray); font-size: 12px;">{conv['role']}</div>
                        <div style="color: var(--linkedin-dark-gray); font-size: 12px;">{conv['last_message']}</div>
                    </div>
                    <div style="margin-left: auto; color: var(--linkedin-dark-gray); font-size: 12px;">{conv['time']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("Chat")
        selected_chat = st.selectbox("Select a conversation", [conv["name"] for conv in conversations])
        
        # Chat messages
        messages = [
            {"sender": "Sarah Johnson", "text": "Hi there! How are you?", "time": "2h ago"},
            {"sender": "You", "text": "I'm good, thanks! How about you?", "time": "1h ago"},
            {"sender": "Sarah Johnson", "text": "Great! Let's meet tomorrow to discuss the project", "time": "30m ago"}
        ]
        
        for msg in messages:
            st.markdown(f"""
            <div style="margin: 8px 0; padding: 8px; background: #f3f2ef; border-radius: 4px; width: fit-content;">
                <div style="font-weight: 600;">{msg['sender']}</div>
                <div style="color: var(--linkedin-dark-gray); font-size: 12px;">{msg['time']}</div>
                <div>{msg['text']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Message input
        new_message = st.text_input("Type a message...")
        if st.button("Send"):
            if new_message:
                st.success("Message sent!")
                messages.append({
                    "sender": "You",
                    "text": new_message,
                    "time": "Just now"
                })
# --- Notifications Page ---
def render_notifications():
    st.title("🔔 Notifications")
    
    # Notification categories
    tab1, tab2, tab3 = st.tabs(["All", "Unread", "Mentions"])
    
    with tab1:
        notifications = [
            {"type": "connection", "text": "John Doe wants to connect with you", "time": "2h ago", "read": False},
            {"type": "like", "text": "Sarah liked your post", "time": "5h ago", "read": True},
            {"type": "comment", "text": "Mike commented on your post", "time": "1d ago", "read": True}
        ]
        
        for notif in notifications:
            st.markdown(f"{'🔵' if not notif['read'] else ''} **{notif['type'].title()}** - {notif['text']} ({notif['time']})")
    
    with tab2:
        unread = [n for n in notifications if not n["read"]]
        for notif in unread:
            st.markdown(f"🔵 **{notif['type'].title()}** - {notif['text']} ({notif['time']})")
    
    with tab3:
        mentions = [n for n in notifications if n["type"] == "mention"]
        if mentions:
            for notif in mentions:
                st.markdown(f"{'🔵' if not notif['read'] else ''} **{notif['type'].title()}** - {notif['text']} ({notif['time']})")
        else:
            st.write("No mentions yet")
# --- Analytics Page ---
def render_analytics():
    st.title("📊 Analytics")
    
    # Profile views
    st.subheader("Profile Views")
    views_data = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=30),
        'Views': np.random.randint(10, 100, size=30)
    })
    st.line_chart(views_data.set_index('Date'))
    
    # Post engagement
    st.subheader("Post Engagement")
    engagement_data = pd.DataFrame({
        'Post': ['Post 1', 'Post 2', 'Post 3'],
        'Likes': [45, 32, 78],
        'Comments': [12, 8, 15],
        'Shares': [5, 3, 10]
    })
    st.bar_chart(engagement_data.set_index('Post'))
    
    # Connection growth
    st.subheader("Connection Growth")
    growth_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
        'Connections': [100, 150, 200, 250]
    })
    st.line_chart(growth_data.set_index('Month'))
# --- Settings Page ---
def render_settings():
    st.title("⚙️ Settings")
    
    # Account settings
    st.subheader("Account Settings")
    with st.form("account_settings"):
        current_email = st.text_input("Email", value=st.session_state.current_user.get("email", ""))
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.form_submit_button("Update Account"):
            if new_password == confirm_password:
                st.success("Account updated successfully!")
            else:
                st.error("Passwords do not match")
    
    # Privacy settings
    st.subheader("Privacy Settings")
    with st.form("privacy_settings"):
        profile_visibility = st.selectbox("Profile Visibility", ["Public", "Connections only", "Private"])
        email_visibility = st.selectbox("Email Visibility", ["Public", "Connections only", "Private"])
        if st.form_submit_button("Update Privacy Settings"):
            st.success("Privacy settings updated!")
    
    # Notification settings
    st.subheader("Notification Settings")
    with st.form("notification_settings"):
        email_notifications = st.checkbox("Email Notifications")
        push_notifications = st.checkbox("Push Notifications")
        connection_requests = st.checkbox("Connection Requests")
        if st.form_submit_button("Update Notification Settings"):
            st.success("Notification settings updated!")
# --- Profile Card ---
def render_profile_card():
    st.markdown(
        """
        <style>
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .card img.cover {
            width: 100%;
            border-radius: 10px 10px 0 0;
        }
        .profile-pic {
            margin-top: -40px;
            display: flex;
            justify-content: center;
        }
        .profile-pic img {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: 2px solid white;
        }
        .university {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 5px;
        }
        .university img {
            width: 20px;
            height: 20px;
            margin-right: 5px;
        }
        hr {
            border: none;
            border-top: 1px solid #e0e0e0;
            margin: 10px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">
            <img class="cover" src="https://images.unsplash.com/photo-1506765515384-028b60a970df">
            <div class="profile-pic">
                <img src=\"""" + LOGO_PATH + """\" style="width: 100px; height: 100px; object-fit: cover;">
            </div>
            <h4 style="text-align:center; margin-top:10px;">""" + st.session_state.current_user["name"] + """</h4>
            <p style="text-align:center; font-size:13px;">""" + st.session_state.current_user["role"] + """</p>
            <p style="text-align:center; font-size:13px;">"""+ st.session_state.current_user["location"]+"""</p>
            <div class="university">
                <img src="https://cdn-icons-png.flaticon.com/512/3073/3073476.png">
                <span style="font-size:13px;">Information Technology University</span>
            </div>
            <hr>
            <div style="font-size:13px; padding:5px 0;">
                <b>Profile viewers</b> <span style="color:blue;">35</span><br>
                <a href="#" style="font-size:12px; color:gray;">View all analytics</a>
            </div>
            <hr>
            <div style="background-color:#f3f2ef; padding:10px; border-radius:8px; font-size:13px;">
                ⭐ <b>Unlock Premium tools & insights</b><br>
                <a href="#" style="font-size:12px; color:#0073b1;">Try Premium for PKR0</a>
            </div>
            <hr>
            <div style="font-size:13px; line-height:2;">
                📦 Saved items<br>
                👥 Groups<br>
                📰 Newsletters<br>
                📅 Events
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
# --- Suggestions Section ---
def render_suggestions():
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-title">Add to your feed</div>
        <div class="sidebar-item">
            <img src=\"""" + LOGO_PATH + """\" style="width: 48px; height: 48px; object-fit: cover;">
            <div class="sidebar-item-content">
                <div class="sidebar-item-title">Sarah Johnson</div>
                <div class="sidebar-item-subtitle">Product Manager at Microsoft</div>
            </div>
            <button class="sidebar-button">Follow</button>
        </div>
        <div class="sidebar-item">
            <img src=\"""" + LOGO_PATH + """\" style="width: 48px; height: 48px; object-fit: cover;">
            <div class="sidebar-item-content">
                <div class="sidebar-item-title">Michael Chen</div>
                <div class="sidebar-item-subtitle">Data Scientist at Netflix</div>
            </div>
            <button class="sidebar-button">Follow</button>
        </div>
    </div>

    <div class="sidebar-card">
        <div class="sidebar-title">Today's top courses</div>
        <div class="sidebar-item">
            <img src=\"""" + LOGO_PATH + """\" style="width: 48px; height: 48px; object-fit: cover;">
            <div class="sidebar-item-content">
                <div class="sidebar-item-title">Machine Learning Fundamentals</div>
                <div class="sidebar-item-subtitle">By Stanford University</div>
            </div>
        </div>
        <div class="sidebar-item">
            <img src=\"""" + LOGO_PATH + """\" style="width: 48px; height: 48px; object-fit: cover;">
            <div class="sidebar-item-content">
                <div class="sidebar-item-title">Product Management 101</div>
                <div class="sidebar-item-subtitle">By Google</div>
            </div>
        </div>
    </div>

    <div class="sidebar-card">
        <div class="sidebar-title">People you may know</div>
        <div class="sidebar-item">
            <img src=\"""" + LOGO_PATH + """\" style="width: 48px; height: 48px; object-fit: cover;">
            <div class="sidebar-item-content">
                <div class="sidebar-item-title">Emily Rodriguez</div>
                <div class="sidebar-item-subtitle">UX Designer at Apple</div>
            </div>
            <button class="sidebar-button">Connect</button>
        </div>
        <div class="sidebar-item">
            <img src=\"""" + LOGO_PATH + """\" style="width: 48px; height: 48px; object-fit: cover;">
            <div class="sidebar-item-content">
                <div class="sidebar-item-title">Alex Brown</div>
                <div class="sidebar-item-subtitle">Software Engineer at Amazon</div>
            </div>
            <button class="sidebar-button">Connect</button>
        </div>
    </div>
    """, unsafe_allow_html=True)


##############################
#### API Integration
##############################
# --- Interactions ---
def send_interaction():
    st.subheader("Simulate User Interaction")
    user_id = st.text_input("User ID", value="U001")
    action_type = st.selectbox("Action", ["Like", "Comment", "Connect"])
    target_id = st.text_input("Target ID (Post ID or User ID)")

    if st.button("Record Interaction"):
        payload = {
            "user_id": user_id,
            "action_type": action_type,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_id": target_id
        }
        response = requests.post("http://localhost:8000/interaction", json=payload)
        st.success(response.json()["status"])

# --- Cache Feed API ---
def cache_feed_api():
    st.subheader("Cache User Feed")
    user_id = st.text_input("User ID for Caching Feed", value="U001")
    posts = st.text_area("Post IDs (comma-separated)", value="Post001,Post002")

    if st.button("Cache Feed"):
        payload = {
            "user_id": user_id,
            "posts": [post.strip() for post in posts.split(",")]
        }
        response = requests.post("http://localhost:8000/cache_feed", json=payload)
        st.success(response.json()["status"])

##############################
##### Main Function
##############################
def main():
    if not render_header():
        return
    
    page = render_sidebar()
    page = st.session_state.current_page
    if page == "Home Feed":
        render_home_feed()
    elif page == "Profile":
        render_profile()
    elif page == "Job Board":
        render_job_board()
    elif page == "Connections":
        render_connections()
    elif page == "Messaging":
        render_messaging()
    elif page == "Notifications":
        render_notifications()
    elif page == "Analytics":
        render_analytics()
    elif page == "Settings":
        render_settings()

# Run the app
if __name__ == "__main__":
    main()