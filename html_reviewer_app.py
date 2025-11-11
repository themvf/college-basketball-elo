import streamlit as st
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="HTML Note Reviewer", page_icon="📝", layout="wide")

st.title("📝 HTML Structured Note Reviewer")
st.markdown("Upload an HTML file to review its structure and content")

# File uploader
uploaded_file = st.file_uploader("Choose an HTML file", type=['html', 'htm'])

if uploaded_file is not None:
    # Read the HTML content
    html_content = uploaded_file.read().decode('utf-8')

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Rendered View", "🔍 HTML Source", "🏗️ Structure Analysis", "📊 Statistics"])

    with tab1:
        st.subheader("Rendered HTML")
        st.markdown("---")
        # Display the rendered HTML
        st.components.v1.html(html_content, height=600, scrolling=True)

    with tab2:
        st.subheader("HTML Source Code")
        st.markdown("---")
        # Display raw HTML
        st.code(html_content, language='html', line_numbers=True)

        # Download button for the HTML
        st.download_button(
            label="Download HTML",
            data=html_content,
            file_name=uploaded_file.name,
            mime="text/html"
        )

    with tab3:
        st.subheader("Document Structure Analysis")
        st.markdown("---")

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract and display structure
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📋 Headings")
            headings = {}
            for level in range(1, 7):
                tags = soup.find_all(f'h{level}')
                if tags:
                    headings[f'h{level}'] = len(tags)
                    with st.expander(f"H{level} ({len(tags)} found)"):
                        for i, tag in enumerate(tags, 1):
                            st.write(f"{i}. {tag.get_text(strip=True)}")

            if not headings:
                st.info("No headings found")

        with col2:
            st.markdown("### 🏷️ Tags Used")
            all_tags = [tag.name for tag in soup.find_all()]
            unique_tags = sorted(set(all_tags))
            tag_counts = {tag: all_tags.count(tag) for tag in unique_tags}

            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
                st.write(f"**`<{tag}>`**: {count}")

        st.markdown("---")

        # Links analysis
        st.markdown("### 🔗 Links")
        links = soup.find_all('a', href=True)
        if links:
            st.write(f"Found {len(links)} links:")
            for i, link in enumerate(links[:20], 1):  # Show first 20 links
                href = link.get('href', '')
                text = link.get_text(strip=True)
                st.write(f"{i}. [{text if text else 'No text'}]({href})")
            if len(links) > 20:
                st.info(f"... and {len(links) - 20} more links")
        else:
            st.info("No links found")

        # Images analysis
        st.markdown("### 🖼️ Images")
        images = soup.find_all('img')
        if images:
            st.write(f"Found {len(images)} images:")
            for i, img in enumerate(images[:10], 1):  # Show first 10 images
                src = img.get('src', 'No source')
                alt = img.get('alt', 'No alt text')
                st.write(f"{i}. `{src}` - Alt: *{alt}*")
            if len(images) > 10:
                st.info(f"... and {len(images) - 10} more images")
        else:
            st.info("No images found")

    with tab4:
        st.subheader("Document Statistics")
        st.markdown("---")

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Calculate statistics
        text_content = soup.get_text()
        words = len(text_content.split())
        characters = len(text_content)
        characters_no_spaces = len(text_content.replace(' ', '').replace('\n', '').replace('\t', ''))

        # Display statistics in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Words", f"{words:,}")
            st.metric("Characters (with spaces)", f"{characters:,}")
            st.metric("Characters (no spaces)", f"{characters_no_spaces:,}")

        with col2:
            paragraphs = len(soup.find_all('p'))
            lists = len(soup.find_all(['ul', 'ol']))
            tables = len(soup.find_all('table'))

            st.metric("Paragraphs", paragraphs)
            st.metric("Lists", lists)
            st.metric("Tables", tables)

        with col3:
            divs = len(soup.find_all('div'))
            spans = len(soup.find_all('span'))
            all_tags = len(soup.find_all())

            st.metric("Div Elements", divs)
            st.metric("Span Elements", spans)
            st.metric("Total HTML Elements", all_tags)

        st.markdown("---")

        # Text preview
        st.markdown("### 📝 Text Content Preview")
        # Clean up text
        clean_text = re.sub(r'\s+', ' ', text_content).strip()
        st.text_area("Extracted Text (first 2000 characters)",
                     clean_text[:2000] + ("..." if len(clean_text) > 2000 else ""),
                     height=200)

else:
    st.info("👆 Please upload an HTML file to begin reviewing")

    # Instructions
    st.markdown("---")
    st.markdown("""
    ### How to use:
    1. Click the "Browse files" button above
    2. Select an HTML file from your computer
    3. Review the content in the different tabs:
       - **Rendered View**: See how the HTML looks when rendered
       - **HTML Source**: View and download the raw HTML code
       - **Structure Analysis**: Examine headings, tags, links, and images
       - **Statistics**: View document metrics and text content
    """)

# Footer
st.markdown("---")
st.markdown("*HTML Structured Note Reviewer - Built with Streamlit*")
