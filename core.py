import re
import pandas as pd
import re
import pandas as pd
from habanero import Crossref

# Initialize Crossref with a polite mailto
cr = Crossref(mailto="25D0222@iitb.ac.in")

def normalise_text(text):
    """Normalize text by converting to lowercase and handling subscripts."""
    if not text:
        return ""

    text = text.lower()

    # Handle subscript characters (₂, ₃, etc.)
    subscript_map = {
        '₂': '2', '₃': '3', '₁': '1', '₀': '0',
        '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'
    }

    for sub, normal in subscript_map.items():
        text = text.replace(sub, normal)

    return text


def check_keyword_match(keyword, text):
    """Smart keyword matching with plural handling."""
    if keyword in text:
        return True
    if keyword.endswith('s') and keyword[:-1] in text:
        return True
    if not keyword.endswith('s') and keyword + "s" in text:
        return True
    return False


def run_search(keywords, threshold, output_limit, progress_callback=None):
    """
    Executes the search using Crossref API.
    
    Args:
        keywords (list): List of keyword strings.
        threshold (int): Minimum number of keywords required to match.
        output_limit (int): Maximum number of papers to find.
        progress_callback (func): Optional callback(scanned_count, match_count).
        
    Returns:
        pd.DataFrame: DataFrame containing relevant papers.
    """
    SEARCH_SPACE_LIMIT = 500 # Matched user snippet (was 50000)
    query_string = " ".join(keywords)
    
    relevant_papers = []
    total_checked = 0
    
    try:
        response_generator = cr.works(
            query_title=query_string,
            filter={'type': 'journal-article'},
            select=['DOI', 'title', 'author', 'abstract', 'issued', 'container-title'],
            sort='relevance',
            order='desc',
            limit=50, # Fetch 50 at a time (matched to user snippet)
            cursor="*",
            cursor_max=SEARCH_SPACE_LIMIT
        )

        for page in response_generator:
            items = page.get('message', {}).get('items', [])
            if not items:
                break

            for item in items:
                total_checked += 1
                
                # Report progress periodically or on every item if needed
                # OPTIMIZATION: Update less frequently to avoid UI bottlenecks (e.g. every 50 items)
                if progress_callback and total_checked % 50 == 0:
                    progress_callback(total_checked, len(relevant_papers))

                if total_checked > SEARCH_SPACE_LIMIT:
                    break

                title = item.get('title', [''])[0]
                if not title:
                    continue

                title_normalized = normalise_text(title)

                matches = []
                for kw in keywords:
                    kw_norm = normalise_text(kw)
                    if check_keyword_match(kw_norm, title_normalized):
                        matches.append(kw)

                if len(set(matches)) >= threshold:
                    relevant_papers.append({
                        'DOI': item.get('DOI'),
                        'Title': title,
                        'Journal': item.get('container-title', [''])[0],
                        'First_Author': item.get('author', [{}])[0].get('family', ''),
                        'Year': item.get('issued', {}).get('date-parts', [[0]])[0][0],
                        'Abstract': item.get('abstract', ''),
                        'Matched_Keywords': ", ".join(matches),
                        'Match_Count': len(matches)
                    })
                
                if len(relevant_papers) >= output_limit:
                    break
            
            if len(relevant_papers) >= output_limit:
                break
            
            if total_checked > SEARCH_SPACE_LIMIT:
                break

    except Exception as e:
        print(f"Error in search: {e}")
        # In a real app we might want to re-raise or handle this differently
        pass
        
    # Final progress update
    if progress_callback:
        progress_callback(total_checked, len(relevant_papers))

    df = pd.DataFrame(relevant_papers)
    if not df.empty:
        df = df.sort_values(['Match_Count', 'Year'], ascending=[False, False])
        
    return df
