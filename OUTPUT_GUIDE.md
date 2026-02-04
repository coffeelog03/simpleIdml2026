# Hướng Dẫn Xem Output IDML trong InDesign

## 📂 Vị Trí Files Output

Các file IDML đã được tạo trong thư mục:
```
/home/user/webapp/output/
```

### Files Có Sẵn

1. **single_text_range.idml** (167K)
   - Một text frame ở giữa page
   - Text: "Hello from simple_idml! This text was created programmatically..."

2. **multiple_text_ranges.idml** (173K)
   - 4 text frames: Header, Left Column, Right Column, Footer
   - Demo layout nhiều cột

3. **positioned_layout.idml** (175K)
   - 5 text frames ở các vị trí: Top Left, Top Right, Center, Bottom Left, Bottom Right
   - Demo positioning thông minh

## 🔧 Cách Mở trong InDesign

### Option 1: Download và Mở Trực Tiếp

```bash
# Copy file từ sandbox về máy local
# Files nằm tại: /home/user/webapp/output/*.idml
```

### Option 2: Tạo Mới từ Script

Chạy script này để tạo files mới:

```bash
cd /home/user/webapp
python3 test_save_output_for_indesign.py
```

Output sẽ được lưu trong thư mục `output/`

## 📋 Nội Dung Các Files

### 1. single_text_range.idml
```
┌─────────────────────────────────┐
│                                 │
│                                 │
│     ┌──────────────────┐       │
│     │ Hello from       │       │
│     │ simple_idml!     │       │
│     │                  │       │
│     │ This text was    │       │
│     │ created          │       │
│     │ programmatically │       │
│     └──────────────────┘       │
│                                 │
│                                 │
└─────────────────────────────────┘
```

### 2. multiple_text_ranges.idml
```
┌─────────────────────────────────────────┐
│ ┌─────────────────────────────────────┐ │
│ │  DOCUMENT HEADER                    │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌──────────┐  ┌──────────────────────┐ │
│ │ Left     │  │ Right Column         │ │
│ │ Column   │  │                      │ │
│ │          │  │ You can position     │ │
│ │ Text...  │  │ text frames          │ │
│ │          │  │ anywhere...          │ │
│ └──────────┘  └──────────────────────┘ │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Page Footer                         │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### 3. positioned_layout.idml
```
┌────────────────────────────────────────┐
│ ┌──────────┐          ┌──────────┐    │
│ │Top Left  │          │Top Right │    │
│ └──────────┘          └──────────┘    │
│                                        │
│            ┌──────────┐                │
│            │ Center   │                │
│            └──────────┘                │
│                                        │
│ ┌──────────┐          ┌──────────┐    │
│ │Bottom    │          │Bottom    │    │
│ │Left      │          │Right     │    │
│ └──────────┘          └──────────┘    │
└────────────────────────────────────────┘
```

## 🔄 Tạo IDML Tùy Chỉnh

Bạn có thể tùy chỉnh script `test_save_output_for_indesign.py` để:

### 1. Thay Đổi Vị Trí Text Frame

```python
# Trong script, tìm dòng này:
center_x = page.coordinates['x1'] + (page_width - frame_width) / 2
center_y = page.coordinates['y1'] + (page_height - frame_height) / 2

# Thay đổi thành vị trí bạn muốn:
center_x = 100  # Vị trí X
center_y = 50   # Vị trí Y
```

### 2. Thay Đổi Kích Thước

```python
# Tìm:
frame_width = 300
frame_height = 150

# Thay đổi:
frame_width = 400   # Chiều rộng mới
frame_height = 200  # Chiều cao mới
```

### 3. Thay Đổi Nội Dung Text

```python
# Tìm:
text_content = "Hello from simple_idml!..."

# Thay đổi:
text_content = "Nội dung text của bạn ở đây"
```

## 📖 Hệ Tọa Độ IDML

IDML sử dụng hệ tọa độ với điểm (0, 0) ở **giữa spread**:

```
        -Y (Top)
         ↑
         |
-X ←─────┼─────→ +X
  (Left) |  (Right)
         |
         ↓
        +Y (Bottom)
```

### Ví Dụ Tọa Độ:

- **Top Left**: x = page.x1 + margin, y = page.y1 + margin
- **Center**: x = (page.x1 + page.x2) / 2, y = (page.y1 + page.y2) / 2
- **Bottom Right**: x = page.x2 - width - margin, y = page.y2 - height - margin

## 🎨 Thông Tin Page Properties

Khi chạy script, bạn sẽ thấy:

```
Page coordinates: {
    'x1': Decimal('0'), 
    'y1': Decimal('-379.84...'), 
    'x2': Decimal('566.92...'), 
    'y2': Decimal('379.84...')
}
```

Với page này:
- **Page width**: 566.93 points
- **Page height**: 759.69 points
- **Center**: (283.46, 0)

## 🛠️ Troubleshooting

### File không mở được trong InDesign?

1. Kiểm tra file có đúng extension `.idml`
2. File size phải > 0 bytes
3. Thử mở với InDesign CC hoặc CS6+

### Text không hiển thị?

1. Kiểm tra text frame có trong đúng layer không
2. Verify story đã được tạo đúng
3. Check coordinates có nằm trong page bounds không

### Muốn xem cấu trúc XML?

```bash
# Giải nén IDML (nó là file ZIP)
cd /home/user/webapp/output
unzip -q single_text_range.idml -d extracted/

# Xem structure
ls -la extracted/
cat extracted/Spreads/Spread_*.xml
cat extracted/Stories/Story_*.xml
```

## 📝 Script Tạo Output Mới

Để tạo thêm file IDML với cấu hình riêng:

```python
# Tạo file mới: my_custom_output.py
import os
import sys
from lxml import etree

sys.path.insert(0, 'src')
from simple_idml.idml import IDMLPackage
from simple_idml.components import Spread, Story

# Mở IDML template
idml = IDMLPackage('test/blank.idml', mode='r')

# Setup working copy
working_copy = 'output/my_working'
os.makedirs(working_copy, exist_ok=True)
idml.extractall(working_copy)
idml.close()

idml = IDMLPackage('test/blank.idml', mode='r')
idml.working_copy_path = working_copy

# Lấy spread và page
spread = idml.spreads_objects[0]
page = spread.pages[0]

# Tạo text frame tùy chỉnh
frame_id = "my_frame"
story_id = "my_story"

textframe_xml = f"""
<TextFrame Self="{frame_id}" 
           ParentStory="{story_id}" 
           ContentType="TextType"
           ItemTransform="1 0 0 1 100 100"
           PreviousTextFrame="n"
           NextTextFrame="n"
           ItemLayer="{idml.designmap.active_layer}">
    <Properties>
        <PathGeometry>
            <GeometryPathType PathOpen="false">
                <PathPointArray>
                    <PathPointType Anchor="0 0" LeftDirection="0 0" RightDirection="0 0"/>
                    <PathPointType Anchor="200 0" LeftDirection="200 0" RightDirection="200 0"/>
                    <PathPointType Anchor="200 100" LeftDirection="200 100" RightDirection="200 100"/>
                    <PathPointType Anchor="0 100" LeftDirection="0 100" RightDirection="0 100"/>
                </PathPointArray>
            </GeometryPathType>
        </PathGeometry>
    </Properties>
    <TextFramePreference TextColumnCount="1" TextColumnMaxWidth="0"/>
</TextFrame>
"""

textframe = etree.fromstring(textframe_xml)
spread.node.append(textframe)

# Tạo story với content
xml_element_id = "my_element"
idml.add_story_with_content(story_id, xml_element_id, "paragraph")

story = Story(idml, f"Stories/Story_{story_id}.xml", working_copy)
story.set_element_content(xml_element_id, "My custom text content!")
story.synchronize()

# Lưu
spread.synchronize()
idml.save('output/my_custom_output.idml')

print("✅ Created: output/my_custom_output.idml")
```

## 🎯 Next Steps

1. **Download files từ sandbox**
2. **Mở trong Adobe InDesign**
3. **Inspect text frames và stories**
4. **Modify script để tạo layouts riêng**
5. **Test với templates khác** (2page.idml, 12page.idml)

## 📞 Support

Nếu cần customize thêm hoặc có vấn đề gì, hãy:
1. Check file TEST_TEXT_RANGE_README.md để xem API reference
2. Xem test_advanced_text_range.py để xem các pattern nâng cao
3. Modify test_save_output_for_indesign.py theo nhu cầu
