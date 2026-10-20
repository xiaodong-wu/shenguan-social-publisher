"""Create a small source-backed social topic plan, without article SEO requirements."""
import re


def build_content_plan(product):
    facts = product['facts']['declared']
    source = facts.get('product_name') or product['title'].split('|')[0]
    phrase = re.sub(r'\bShenguan(?:\s+Watch)?\b|\bSGW-[A-Z0-9-]+\b', '', source, flags=re.I)
    phrase = re.sub(r'\s+', ' ', phrase).strip(' -|')
    topics = ('automatic diving watch', 'automatic dive watch', 'diving watch', 'dive watch',
              'quartz watches', 'quartz watch', 'wooden watches', 'wooden watch',
              'chronograph watch', 'iced out watches', 'automatic watch', 'mechanical watch')
    phrase = next((m.group(0) for t in topics if (m := re.search(r'\b'+re.escape(t)+r'\b', phrase, re.I))), phrase)
    if not 2 <= len(phrase.split()) <= 16:
        raise ValueError('Product has no natural, source-backed social topic')
    return {
        'core_keyword': phrase, 'source_text': source,
        'source_url': product['canonical_url'],
        'related_topics': product.get('use_cases', [])[:4],
        'buyer_intent': 'product evaluation and sourcing inquiry',
        'instructions': 'Preserve option qualifiers. Trace all claims to product evidence; do not infer final configuration or diving depth.',
    }
