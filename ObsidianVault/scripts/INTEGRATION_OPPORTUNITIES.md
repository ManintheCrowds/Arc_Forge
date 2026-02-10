# Integration Opportunities

## Purpose
Comprehensive guide to Obsidian plugin and external API integration opportunities for the PDF ingestion system.

---

## 1. Obsidian Plugin Integrations

### PDF++ Plugin Integration

**Plugin**: PDF++ by Ryota Ushio  
**GitHub**: https://github.com/RyotaUshio/obsidian-pdf-plus

#### Integration Points

1. **Annotation Extraction**
   - Read annotations from PDF++ cache
   - Extract highlights, comments, free text
   - Preserve annotation metadata (color, page, type)

2. **Bidirectional Linking**
   - Link annotations to source notes
   - Link source notes back to PDF annotations
   - Create entity notes from annotations

3. **Text Cache Integration**
   - Already integrated for text extraction
   - Enhance with annotation data
   - Sync annotation updates

#### Implementation Approach

```python
# Pseudo-code for annotation extraction
def extract_pdfplus_annotations(pdf_path, vault_root):
    # Find PDF++ cache directory
    cache_dir = find_pdfplus_cache(vault_root)
    
    # Read annotation data
    annotations = read_annotations_from_cache(cache_dir, pdf_path)
    
    # Convert to note format
    annotation_sections = format_annotations_for_notes(annotations)
    
    # Link to source note
    link_annotations_to_source_note(annotation_sections, source_note)
    
    # Create entity notes from annotations
    create_entity_notes_from_annotations(annotations)
```

#### Benefits
- Connects reading and note-taking workflows
- Preserves annotation context
- Enables bidirectional navigation
- Reduces manual work

#### Effort: Medium
- Requires understanding PDF++ cache structure
- Annotation format parsing
- Link generation

---

### Dataview Plugin Integration

**Plugin**: Dataview by Michael Brenan

#### Integration Points

1. **Dynamic Indexes**
   - Query ingested sources
   - Generate filtered views
   - Statistics and analytics

2. **Entity Relationships**
   - Query entity connections
   - Generate relationship graphs
   - Filter by entity type

3. **Source Analysis**
   - Query sources by metadata
   - Generate reports
   - Track ingestion statistics

#### Implementation Approach

```markdown
# Example Dataview queries for ingested sources
```dataview
TABLE doc_type, created, tags
FROM "Sources"
WHERE doc_type != "unverified"
SORT created DESC
```

```dataview
LIST
FROM "NPCs"
WHERE contains(source_refs, "[[Source Name]]")
```
```

#### Benefits
- Advanced filtering and querying
- Dynamic index generation
- Statistics and analytics
- No code changes needed (markdown queries)

#### Effort: Low
- No code integration needed
- Users write Dataview queries
- Document query patterns

---

### Templater Plugin Integration

**Plugin**: Templater by SilentVoid

#### Integration Points

1. **Enhanced Templates**
   - Dynamic template processing
   - Conditional logic
   - Variable substitution

2. **Template Functions**
   - Date formatting
   - Entity counting
   - Source statistics

3. **Template Inheritance**
   - Base templates
   - Template composition
   - Reusable components

#### Implementation Approach

```markdown
# Enhanced source note template with Templater
<%*
const title = tp.file.title;
const sourceFile = await tp.system.prompt("Source file path?");
const docType = await tp.system.suggester(
    ["Rulebook", "Adventure", "Supplement", "Other"],
    ["rulebook", "adventure", "supplement", "other"]
);
-%>
---
title: "<% title %>"
source_file: "<% sourceFile %>"
doc_type: "<% docType %>"
created: "<% tp.date.now("YYYY-MM-DD") %>"
---
```

#### Benefits
- More flexible templates
- User interaction during note creation
- Dynamic content generation
- Better user experience

#### Effort: Low
- Template modifications only
- No code changes needed
- Document template patterns

---

### Tag Wrangler Plugin Integration

**Plugin**: Tag Wrangler by P.J. Eby

#### Integration Points

1. **Auto-Tagging**
   - Suggest tags from content
   - Auto-apply tags
   - Tag suggestions

2. **Tag Management**
   - Tag renaming
   - Tag hierarchy
   - Tag cleanup

#### Implementation Approach

```python
# Auto-tagging based on content
def suggest_tags(text, doc_type):
    tags = []
    
    # Extract keywords
    keywords = extract_keywords(text)
    
    # Map to tags
    for keyword in keywords:
        tag = map_keyword_to_tag(keyword)
        if tag:
            tags.append(tag)
    
    # Add doc_type tag
    tags.append(f"type/{doc_type}")
    
    return tags
```

#### Benefits
- Automatic tag suggestions
- Consistent tagging
- Better organization
- Reduced manual work

#### Effort: Low-Medium
- Keyword extraction
- Tag mapping logic
- Integration with note creation

---

### Citations Plugin Integration

**Plugin**: Citations by Jon Gauthier

#### Integration Points

1. **Citation Linking**
   - Link source notes to Zotero references
   - Generate citation links
   - Bibliography generation

2. **Citation Format**
   - BibTeX import
   - Citation formatting
   - Reference management

#### Implementation Approach

```python
# Link source note to Zotero reference
def link_to_zotero(source_note, zotero_id):
    # Add Zotero link to frontmatter
    frontmatter = read_frontmatter(source_note)
    frontmatter["zotero_id"] = zotero_id
    write_frontmatter(source_note, frontmatter)
    
    # Create citation link
    citation_link = f"[[@zotero:{zotero_id}]]"
    append_to_note(source_note, citation_link)
```

#### Benefits
- Academic workflow integration
- Citation management
- Bibliography generation
- Reference linking

#### Effort: Medium
- Zotero API integration
- Citation format support
- Link generation

---

## 2. External API Integrations

### OpenAI/Claude API Integration

#### Use Cases

1. **Document Summarization**
   - Generate summaries
   - Extract key points
   - Create executive summaries

2. **Entity Extraction**
   - Extract NPCs, factions, locations
   - Identify rules and mechanics
   - Structured entity data

3. **Question Answering**
   - Answer questions about PDFs
   - Extract specific information
   - Generate insights

#### Implementation Approach

```python
# LLM summarization
def summarize_with_llm(text, api_key, model="gpt-4"):
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes RPG rulebooks."},
            {"role": "user", "content": f"Summarize this text:\n\n{text}"}
        ],
        max_tokens=500
    )
    
    return response.choices[0].message.content
```

#### Benefits
- High-quality summaries
- Automatic entity extraction
- Question answering
- Content insights

#### Effort: Medium-High
- API integration
- Cost management
- Error handling
- Rate limiting

#### Cost Considerations
- OpenAI GPT-4: ~$0.03 per 1K tokens
- Claude: Similar pricing
- Local LLM (Ollama): Free but requires hardware

---

### Tesseract OCR Integration

#### Use Cases

1. **Scanned PDF Processing**
   - OCR for image-based PDFs
   - Text extraction from scans
   - Multi-language support

2. **Layout Detection**
   - Multi-column detection
   - Table recognition
   - Structure preservation

#### Implementation Approach

```python
# OCR with Tesseract
def ocr_pdf(pdf_path):
    import pytesseract
    from pdf2image import convert_from_path
    
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    
    # OCR each page
    text_pages = []
    for image in images:
        text = pytesseract.image_to_string(image)
        text_pages.append(text)
    
    return "\n".join(text_pages)
```

#### Benefits
- Enables scanned PDF processing
- Multi-language support
- Free and open source
- Self-hosted option

#### Effort: Medium
- Tesseract installation
- Image conversion
- Layout detection
- Error handling

---

### Zotero API Integration

#### Use Cases

1. **Metadata Sync**
   - Import PDF metadata from Zotero
   - Sync citation information
   - Link to Zotero references

2. **Citation Management**
   - Generate citations
   - Export to BibTeX
   - Reference linking

#### Implementation Approach

```python
# Zotero API integration
def get_zotero_metadata(zotero_id, api_key):
    import requests
    
    url = f"https://api.zotero.org/users/{user_id}/items/{zotero_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    return {
        "title": data["data"]["title"],
        "authors": data["data"].get("creators", []),
        "date": data["data"].get("date", ""),
        "doi": data["data"].get("DOI", "")
    }
```

#### Benefits
- Academic workflow integration
- Automatic metadata extraction
- Citation management
- Reference linking

#### Effort: Medium
- Zotero API understanding
- Authentication
- Data mapping
- Error handling

---

### Obsidian URI API Integration

#### Use Cases

1. **Programmatic Note Creation**
   - Create notes from external tools
   - Update notes programmatically
   - Link notes automatically

2. **External Tool Integration**
   - Trigger from other applications
   - Cross-application workflows
   - Automation integration

#### Implementation Approach

```python
# Create note via Obsidian URI
def create_note_via_uri(vault_name, note_path, content):
    import urllib.parse
    
    # Encode content
    encoded_content = urllib.parse.quote(content)
    
    # Build URI
    uri = f"obsidian://new?vault={vault_name}&file={note_path}&content={encoded_content}"
    
    # Open URI (triggers Obsidian)
    import subprocess
    subprocess.run(["start", uri], shell=True)
```

#### Benefits
- External tool integration
- Automation workflows
- Cross-application workflows
- Programmatic note management

#### Effort: Low
- URI format understanding
- Encoding handling
- Platform-specific execution

---

## 3. Integration Architecture

### Plugin Integration Pattern

```
PDF Ingestion System
    ↓
Obsidian Plugins (PDF++, Dataview, etc.)
    ↓
Obsidian Vault
    ↓
Enhanced Notes & Links
```

### API Integration Pattern

```
PDF Ingestion System
    ↓
External APIs (OpenAI, Zotero, OCR)
    ↓
Enhanced Processing
    ↓
Obsidian Vault
```

### Hybrid Integration Pattern

```
PDF Ingestion System
    ├─→ Obsidian Plugins (read annotations, query data)
    ├─→ External APIs (AI, OCR, citations)
    └─→ Obsidian Vault (enhanced notes)
```

---

## 4. Integration Priority Matrix

| Integration | User Value | Implementation Effort | Dependencies | Priority |
|-------------|------------|---------------------|--------------|----------|
| PDF++ Annotation Extraction | High | Medium | PDF++ plugin | 1 |
| OpenAI/Claude Summarization | Very High | Medium-High | API key, cost | 2 |
| Zotero Metadata Sync | Medium-High | Medium | Zotero API | 3 |
| Tesseract OCR | Very High | Medium | Tesseract install | 4 |
| Dataview Queries | Medium | Low | Dataview plugin | 5 |
| Templater Enhancement | Medium | Low | Templater plugin | 6 |
| Obsidian URI API | Medium | Low | URI format | 7 |
| Tag Wrangler Auto-Tagging | Medium | Low-Medium | Tag Wrangler | 8 |

---

## 5. Implementation Roadmap

### Phase 1: Core Integrations
1. PDF++ Annotation Extraction
2. Tesseract OCR
3. Event-Driven Processing

### Phase 2: AI Integration
1. OpenAI/Claude Summarization
2. LLM Entity Extraction
3. Question Answering

### Phase 3: Academic Workflows
1. Zotero Integration
2. Citation Management
3. BibTeX Export

### Phase 4: Plugin Enhancements
1. Dataview Query Documentation
2. Templater Template Library
3. Tag Wrangler Auto-Tagging

---

## 6. Integration Examples

### Example 1: PDF++ Annotation Extraction

```python
# Extract annotations from PDF++ and create note sections
def integrate_pdfplus_annotations(pdf_path, source_note_path):
    # Find PDF++ cache
    cache_dir = find_pdfplus_cache(vault_root)
    annotations = read_annotations(cache_dir, pdf_path)
    
    # Create annotation sections
    annotation_content = "## Annotations\n\n"
    for ann in annotations:
        annotation_content += f"- **Page {ann.page}**: {ann.text}\n"
        annotation_content += f"  - Color: {ann.color}\n"
        annotation_content += f"  - Type: {ann.type}\n\n"
    
    # Append to source note
    append_to_note(source_note_path, annotation_content)
```

### Example 2: LLM Summarization

```python
# Summarize PDF with OpenAI
def summarize_pdf_with_ai(pdf_text, api_key):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    Summarize this RPG rulebook section. Extract:
    1. Key rules and mechanics
    2. Important NPCs, factions, locations
    3. Main plot points or setting details
    
    Text:
    {pdf_text[:4000]}  # Limit to avoid token limits
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    
    return response.choices[0].message.content
```

### Example 3: Zotero Metadata Sync

```python
# Sync metadata from Zotero
def sync_zotero_metadata(source_note_path, zotero_id):
    metadata = get_zotero_metadata(zotero_id, api_key)
    
    # Update frontmatter
    frontmatter = read_frontmatter(source_note_path)
    frontmatter.update({
        "title": metadata["title"],
        "authors": metadata["authors"],
        "date": metadata["date"],
        "doi": metadata.get("doi", ""),
        "zotero_id": zotero_id
    })
    
    write_frontmatter(source_note_path, frontmatter)
```

---

## 7. Integration Testing

### Test Scenarios

1. **PDF++ Integration**
   - Extract annotations from test PDF
   - Verify annotation linking
   - Test bidirectional navigation

2. **OCR Integration**
   - Process scanned PDF
   - Verify text extraction quality
   - Test layout detection

3. **LLM Integration**
   - Generate summary
   - Extract entities
   - Test error handling

4. **Zotero Integration**
   - Sync metadata
   - Link references
   - Test citation export

---

## 8. Integration Documentation

### User Guides Needed

1. **PDF++ Integration Guide**: How to use annotation extraction
2. **OCR Setup Guide**: Installing and configuring Tesseract
3. **LLM Integration Guide**: Setting up API keys and costs
4. **Zotero Integration Guide**: Connecting to Zotero library
5. **Plugin Integration Guide**: Using Dataview, Templater, etc.

### Developer Documentation

1. **Integration API**: How to add new integrations
2. **Plugin Architecture**: How plugins interact
3. **API Patterns**: Common integration patterns
4. **Error Handling**: Integration error handling

---

## Summary

### High-Value Integrations
- PDF++ Annotation Extraction
- OpenAI/Claude Summarization
- Tesseract OCR
- Zotero Metadata Sync

### Low-Effort Integrations
- Dataview Queries
- Templater Templates
- Obsidian URI API
- Tag Wrangler Auto-Tagging

### Recommended Implementation Order
1. PDF++ (connects reading workflow)
2. OCR (enables scanned PDFs)
3. LLM (adds intelligence)
4. Zotero (academic workflows)
5. Plugin enhancements (user experience)
