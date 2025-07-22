import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load original data once
df_original = pd.read_csv("cleaned_data.csv")

st.set_page_config(page_title="Swiggy Restaurant Explorer", layout="wide")
st.title("🍴 Swiggy Restaurant Explorer")

# Sidebar page selector
page = st.sidebar.radio("Choose Page", ["Explore Restaurants", "Dashboard"])

if page == "Explore Restaurants":
    # --- Page 1: Filter page with multi-select city and cuisine ---

    df = df_original.copy()

    st.sidebar.header("🎯 Apply Filters")

    # City Filter (multi-select, no default selection)
    if 'city' in df.columns:
        cities = sorted(df['city'].dropna().unique())
        selected_cities = st.sidebar.multiselect("Select City(s)", options=cities, key="city_filter")
        if selected_cities:
            df = df[df['city'].isin(selected_cities)].copy()

    # Rating Filter (single min slider)
    if 'rating' in df.columns:
        min_rating = st.sidebar.slider("Minimum Rating ⭐", 0.0, 5.0, 3.0, step=0.1, key="rating_filter")
        df = df[df['rating'] >= min_rating].copy()

    # Cost Filter (minimum only)
    if 'cost' in df_original.columns:
        original_min_cost = int(df_original['cost'].min())
        min_cost = st.sidebar.number_input("Minimum Cost (₹)", value=original_min_cost, step=10, key="cost_filter")
        df = df[df['cost'] >= min_cost].copy()

    # Cuisine Filter (multi-select, no default selection)
    if 'cuisine' in df.columns:
        cuisines = sorted(df['cuisine'].dropna().unique())
        selected_cuisines = st.sidebar.multiselect("🍱 Select Cuisine(s)", options=cuisines, key="cuisine_filter")
        if selected_cuisines:
            df = df[df['cuisine'].isin(selected_cuisines)].copy()

    if not df.empty:
        st.write(f"Total Restaurants Found: {len(df)}")
        df_sorted = df.sort_values(by=["rating", "cost"], ascending=[False, True])
        top_df = df_sorted.head(10).copy()

        def rating_emoji(r):
            if r >= 4.5:
                return "🌟"
            elif r >= 4.0:
                return "👍"
            elif r >= 3.5:
                return "👌"
            else:
                return "🙂"

        top_df["Rating"] = top_df["rating"].apply(lambda x: f"{x:.1f} {rating_emoji(x)}")

        st.subheader("🏆 Top 3 Restaurants")
        top3 = top_df.head(3)
        cols = st.columns(3)
        for idx, row in enumerate(top3.itertuples()):
            with cols[idx]:
                st.markdown(f"""
                    #### 🍽️ **{row.name}**
                    **📍 City:** {row.city}  
                    **⭐ Rating:** {row.Rating}  
                    **💰 Cost:** ₹{int(row.cost)}  
                    **🍛 Cuisine:** {row.cuisine}  
                    **📌 Address:** {row.address}
                """)

        st.markdown("---")
        st.subheader("📊 Top 10 Filtered Restaurants")
        display_df = top_df[["name", "city", "cost", "Rating", "cuisine", "address"]]
        display_df.columns = ["Restaurant Name", "City", "Cost (₹)", "Rating", "Cuisine", "Address"]

        st.dataframe(display_df.reset_index(drop=True), use_container_width=True)

    else:
        st.warning("No matching restaurants found. Please adjust your filters.")

elif page == "Dashboard":
    # --- Page 2: Dashboard with filters + visualizations ---

    df = df_original.copy()

    st.sidebar.header("📊 Dashboard Filters")

    # City Filter (multi-select, no default selection)
    if 'city' in df.columns:
        cities = sorted(df['city'].dropna().unique())
        selected_cities = st.sidebar.multiselect("Select City(s)", options=cities, key="dash_city")
        if selected_cities:
            df = df[df['city'].isin(selected_cities)].copy()

    # Cuisine Filter (multi-select, no default selection)
    if 'cuisine' in df.columns:
        cuisines = sorted(df['cuisine'].dropna().unique())
        selected_cuisines = st.sidebar.multiselect("Select Cuisine(s)", options=cuisines, key="dash_cuisine")
        if selected_cuisines:
            df = df[df['cuisine'].isin(selected_cuisines)].copy()

    # Rating Filter (single min slider)
    if 'rating' in df.columns:
        min_rating = st.sidebar.slider("Minimum Rating ⭐", 0.0, 5.0, 0.0, step=0.1, key="dash_rating")
        df = df[df['rating'] >= min_rating].copy()

    # Cost Filter (minimum only)
    if 'cost' in df.columns:
        min_cost_default = int(df['cost'].min())
        min_cost = st.sidebar.number_input("Minimum Cost (₹)", value=min_cost_default, step=10, key="dash_cost")
        df = df[df['cost'] >= min_cost].copy()

    st.write(f"### Filtered Restaurants Count: {len(df)}")

    if df.empty:
        st.warning("No restaurants found with selected filters.")
    else:
        # Rating Distribution Histogram
        st.subheader("⭐ Rating Distribution")
        fig, ax = plt.subplots()
        sns.histplot(df['rating'], bins=20, kde=True, ax=ax)
        st.pyplot(fig)

        # Cost vs Rating Scatter Plot
        st.subheader("💰 Cost vs ⭐ Rating")
        fig2, ax2 = plt.subplots()
        sns.scatterplot(data=df, x='cost', y='rating', hue='cuisine', palette='tab10', ax=ax2)
        ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
        st.pyplot(fig2)

        # Restaurants count by City Bar Plot (top 20 only)
        st.subheader("🏙️ Restaurants Count by City")
        top_n_cities = 20
        city_counts = df['city'].value_counts().head(top_n_cities)
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.barplot(x=city_counts.index, y=city_counts.values, ax=ax3)
        ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right')
        st.pyplot(fig3)

        # Top cuisines pie chart (top 10 only)
        st.subheader("🍽️ Top Cuisines Distribution")
        top_n_cuisines = 10
        cuisine_counts = df['cuisine'].value_counts().head(top_n_cuisines)
        fig4, ax4 = plt.subplots(figsize=(7, 7))
        ax4.pie(cuisine_counts, labels=cuisine_counts.index, autopct='%1.1f%%', startangle=140)
        ax4.axis('equal')
        st.pyplot(fig4)
