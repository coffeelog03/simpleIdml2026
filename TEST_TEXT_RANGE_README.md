# Test: Adding TextRanges to Spread->Page in IDML

Các file test này minh họa cách thêm text ranges (TextFrame elements) vào cấu trúc spread->page trong file IDML, sử dụng các class và method có sẵn từ module `simple_idml.idml` và `simple_idml.components`.

## Files

### 1. `test_add_text_range.py`
Test cơ bản để thêm text ranges vào IDML document.

**Chức năng:**
- Test thêm một text range đơn lẻ
- Test thêm nhiều text ranges
- Sử dụng các class: `IDMLPackage`, `Spread`, `Story`, `Page`

**Chạy test:**
```bash
python3 test_add_text_range.py
```

### 2. `test_advanced_text_range.py`
Test nâng cao với helper class và positioning thông minh.

**Chức năng:**
- `TextRangeBuilder` helper class để quản lý text ranges
- Smart positioning sử dụng Page properties
- Demo truy cập và đọc các component có sẵn

**Chạy test:**
```bash
python3 test_advanced_text_range.py
```

## Các Class và Method Chính

### IDMLPackage (từ simple_idml.idml)
```python
# Mở IDML package
idml = IDMLPackage('path/to/file.idml', mode='r')

# Properties
idml.spreads_objects          # Danh sách các Spread objects
idml.spreads                  # Danh sách tên file spreads
idml.stories                  # Danh sách tên file stories
idml.story_ids                # Danh sách story IDs
idml.pages                    # Danh sách tất cả pages
idml.designmap                # Designmap object
idml.tags                     # Danh sách tags

# Methods
idml.add_story_with_content(story_id, xml_element_id, xml_element_tag)
idml.save(path)               # Lưu IDML
```

### Spread (từ simple_idml.components)
```python
spread = idml.spreads_objects[0]

# Properties
spread.name                   # Tên file spread
spread.pages                  # Danh sách Page objects
spread.node                   # etree element của spread
spread.dom                    # etree DOM của spread

# Methods
spread.add_page(page)         # Thêm page
spread.get_element_by_id(id)  # Lấy element theo ID
spread.synchronize()          # Lưu thay đổi
```

### Page (từ simple_idml.components)
```python
page = spread.pages[0]

# Properties
page.coordinates              # Dict với x1, y1, x2, y2
page.geometric_bounds         # Boundaries của page
page.item_transform           # Transform matrix
page.face                     # 'recto' hoặc 'verso'
page.is_recto                 # Boolean
page.page_items               # Danh sách items trên page

# Methods
page.set_face(face)           # Đặt face (recto/verso)
```

### Story (từ simple_idml.components)
```python
story = Story(idml, story_name, working_copy_path)

# Properties
story.name                    # Tên file story
story.node                    # etree node của story

# Methods
story.set_element_content(element_id, content)
story.get_element_by_id(element_id)
story.add_element(destination_id, element)
story.synchronize()
```

### XMLElement (từ simple_idml.components)
```python
xml_element = XMLElement(tag='paragraph')

# Methods
xml_element.set_content(content)
xml_element.set_attribute(name, value)
xml_element.set_attributes(dict)
xml_element.get_attribute(name)
xml_element.add_content(content, parent, style_range_node)
```

## Workflow Cơ Bản

### 1. Mở IDML Package với Working Copy
```python
from simple_idml.idml import IDMLPackage

# Mở file
idml = IDMLPackage('input.idml', mode='r')

# Tạo working copy
working_copy_path = '/tmp/working_copy'
os.makedirs(working_copy_path, exist_ok=True)
idml.extractall(working_copy_path)
idml.close()

# Mở lại với working copy
idml = IDMLPackage('input.idml', mode='r')
idml.working_copy_path = working_copy_path
```

### 2. Truy Cập Spread và Page
```python
# Lấy spread đầu tiên
spread = idml.spreads_objects[0]

# Lấy page đầu tiên
page = spread.pages[0]

# Xem thông tin page
print(f"Page coordinates: {page.coordinates}")
print(f"Page face: {page.face}")
```

### 3. Tạo TextFrame Element
```python
from lxml import etree

# Định nghĩa vị trí và kích thước
frame_id = "my_textframe"
story_id = "my_story"
x, y = 100, 100
width, height = 200, 100

# Tạo TextFrame XML
textframe_xml = f"""
<TextFrame Self="{frame_id}" 
           ParentStory="{story_id}" 
           ContentType="TextType"
           ItemTransform="1 0 0 1 {x} {y}"
           PreviousTextFrame="n"
           NextTextFrame="n"
           ItemLayer="{idml.designmap.active_layer}">
    <Properties>
        <PathGeometry>
            <GeometryPathType PathOpen="false">
                <PathPointArray>
                    <PathPointType Anchor="0 0" LeftDirection="0 0" RightDirection="0 0"/>
                    <PathPointType Anchor="{width} 0" LeftDirection="{width} 0" RightDirection="{width} 0"/>
                    <PathPointType Anchor="{width} {height}" LeftDirection="{width} {height}" RightDirection="{width} {height}"/>
                    <PathPointType Anchor="0 {height}" LeftDirection="0 {height}" RightDirection="0 {height}"/>
                </PathPointArray>
            </GeometryPathType>
        </PathGeometry>
    </Properties>
    <TextFramePreference TextColumnCount="1" TextColumnMaxWidth="0"/>
</TextFrame>
"""

textframe = etree.fromstring(textframe_xml)
```

### 4. Thêm TextFrame vào Spread
```python
# Thêm vào spread node
spread.node.append(textframe)
```

### 5. Tạo Story và Thêm Content
```python
from simple_idml.components import Story

# Tạo story
xml_element_id = "xmlelem_001"
xml_element_tag = "paragraph"

idml.add_story_with_content(story_id, xml_element_id, xml_element_tag)

# Lấy story và set content
story_name = f"Stories/Story_{story_id}.xml"
story = Story(idml, story_name, working_copy_path)

text_content = "Hello from simple_idml!"
story.set_element_content(xml_element_id, text_content)
story.synchronize()
```

### 6. Lưu Thay Đổi
```python
# Synchronize spread
spread.synchronize()

# Lưu IDML package
idml.save('output.idml')
```

## Positioning Thông Minh

### Sử Dụng Page Coordinates
```python
# Lấy kích thước page
page_width = page.coordinates['x2'] - page.coordinates['x1']
page_height = page.coordinates['y2'] - page.coordinates['y1']

# Căn giữa
center_x = page.coordinates['x1'] + (page_width - frame_width) / 2
center_y = page.coordinates['y1'] + (page_height - frame_height) / 2

# Top-left với margin
margin = 50
top_left_x = page.coordinates['x1'] + margin
top_left_y = page.coordinates['y1'] + margin

# Bottom-right với margin
bottom_right_x = page.coordinates['x2'] - frame_width - margin
bottom_right_y = page.coordinates['y2'] - frame_height - margin
```

## Helper Class Pattern

```python
class TextRangeBuilder:
    """Helper class để quản lý text ranges"""
    
    def __init__(self, idml_package, spread):
        self.idml = idml_package
        self.spread = spread
        self.active_layer = idml_package.designmap.active_layer
        self.working_copy_path = idml_package.working_copy_path
    
    def add_text_range(self, frame_id, story_id, text_content, x, y, width=200, height=100):
        """Thêm text range hoàn chỉnh"""
        # 1. Tạo TextFrame
        textframe = self.create_textframe(frame_id, story_id, x, y, width, height)
        
        # 2. Thêm vào spread
        self.spread.node.append(textframe)
        
        # 3. Tạo story
        xml_element_id = f"xmlelem_{frame_id}"
        self.idml.add_story_with_content(story_id, xml_element_id, "paragraph")
        
        # 4. Set content
        story = Story(self.idml, f"Stories/Story_{story_id}.xml", self.working_copy_path)
        story.set_element_content(xml_element_id, text_content)
        story.synchronize()
        
        return textframe, story
    
    def save(self):
        """Lưu tất cả thay đổi"""
        self.spread.synchronize()
```

Sử dụng:
```python
builder = TextRangeBuilder(idml, spread)
builder.add_text_range('frame1', 'story1', 'Hello World', 100, 100)
builder.save()
```

## Lưu Ý

1. **Working Copy**: Luôn sử dụng working copy để thay đổi IDML
2. **Synchronize**: Gọi `synchronize()` sau khi thay đổi Story hoặc Spread
3. **Unique IDs**: Đảm bảo frame_id và story_id là duy nhất
4. **Coordinates**: IDML sử dụng hệ tọa độ với (0,0) ở giữa spread
5. **Layer**: Luôn set ItemLayer cho TextFrame

## Kết Quả Test

```
============================================================
Test Results:
  Single TextRange Test: PASSED
  Multiple TextRanges Test: PASSED
============================================================

============================================================
Test Summary:
============================================================
✓ PASSED: TextRangeBuilder Helper Class
✓ PASSED: Smart Page Positioning
✓ PASSED: Accessing Existing Components
============================================================
```

## Tài Liệu Tham Khảo

- Module `simple_idml.idml`: Chứa class `IDMLPackage`
- Module `simple_idml.components`: Chứa các class `Spread`, `Story`, `Page`, `XMLElement`, `Designmap`
- Test files IDML: `test/blank.idml`, `test/2page.idml`
