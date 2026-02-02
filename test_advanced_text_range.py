# -*- coding: utf-8 -*-

"""
Advanced Test: Adding TextRanges to Spread->Page using Simple IDML API

This test demonstrates best practices for working with:
- IDMLPackage class (from simple_idml.idml)
- Spread class (from simple_idml.components)
- Page class (from simple_idml.components)
- Story class (from simple_idml.components)
- XMLElement class (from simple_idml.components)

Key Methods Used:
=================
1. IDMLPackage:
   - spreads_objects: Access all spread objects
   - add_story_with_content(): Create new story with content
   - save(): Save modified IDML package

2. Spread:
   - pages: List of Page objects in the spread
   - node: etree element of the spread
   - synchronize(): Save changes to disk

3. Page:
   - coordinates: Dictionary with x1, y1, x2, y2 coordinates
   - geometric_bounds: Page boundaries
   - face: Page face (recto/verso)
   - is_recto: Boolean indicating page side

4. Story:
   - set_element_content(): Set text content for an element
   - get_element_by_id(): Get element by ID
   - synchronize(): Save changes to disk

5. XMLElement:
   - set_attribute(): Set attribute on element
   - set_content(): Set text content
"""

import os
import sys
import tempfile
import shutil
from decimal import Decimal
from lxml import etree

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simple_idml.idml import IDMLPackage
from simple_idml.components import Spread, Story, Page, XMLElement


class TextRangeBuilder:
    """
    Helper class to build TextFrame elements (text ranges) for IDML documents.
    
    This demonstrates a clean pattern for working with simple_idml classes.
    """
    
    def __init__(self, idml_package, spread):
        """
        Initialize the builder.
        
        Args:
            idml_package: IDMLPackage instance
            spread: Spread instance
        """
        self.idml = idml_package
        self.spread = spread
        self.active_layer = idml_package.designmap.active_layer
        self.working_copy_path = idml_package.working_copy_path
    
    def create_textframe(self, frame_id, story_id, x, y, width, height):
        """
        Create a TextFrame element using IDML structure.
        
        Args:
            frame_id: Unique ID for the TextFrame
            story_id: ID of the story to link
            x, y: Position coordinates
            width, height: Frame dimensions
            
        Returns:
            etree.Element: TextFrame element
        """
        # Build the TextFrame XML structure
        textframe_xml = f"""
        <TextFrame Self="{frame_id}" 
                   ParentStory="{story_id}" 
                   ContentType="TextType"
                   ItemTransform="1 0 0 1 {x} {y}"
                   PreviousTextFrame="n"
                   NextTextFrame="n"
                   ItemLayer="{self.active_layer}"
                   Visible="true">
            <Properties>
                <PathGeometry>
                    <GeometryPathType PathOpen="false">
                        <PathPointArray>
                            <PathPointType Anchor="0 0" 
                                         LeftDirection="0 0" 
                                         RightDirection="0 0"/>
                            <PathPointType Anchor="{width} 0" 
                                         LeftDirection="{width} 0" 
                                         RightDirection="{width} 0"/>
                            <PathPointType Anchor="{width} {height}" 
                                         LeftDirection="{width} {height}" 
                                         RightDirection="{width} {height}"/>
                            <PathPointType Anchor="0 {height}" 
                                         LeftDirection="0 {height}" 
                                         RightDirection="0 {height}"/>
                        </PathPointArray>
                    </GeometryPathType>
                </PathGeometry>
            </Properties>
            <TextFramePreference TextColumnCount="1" TextColumnMaxWidth="0"/>
        </TextFrame>
        """
        
        return etree.fromstring(textframe_xml)
    
    def add_text_range(self, frame_id, story_id, text_content, x, y, width=200, height=100):
        """
        Add a complete text range (TextFrame + Story) to the spread.
        
        This method demonstrates the complete workflow:
        1. Create TextFrame element
        2. Add to spread
        3. Create story with content
        4. Set text content
        5. Synchronize changes
        
        Args:
            frame_id: Unique ID for the TextFrame
            story_id: Unique ID for the story
            text_content: Text to add to the frame
            x, y: Position coordinates
            width, height: Frame dimensions (optional)
            
        Returns:
            tuple: (textframe_element, story)
        """
        # Step 1: Create TextFrame element
        textframe = self.create_textframe(frame_id, story_id, x, y, width, height)
        
        # Step 2: Add to spread node
        self.spread.node.append(textframe)
        
        # Step 3: Create story with XML element
        xml_element_id = f"xmlelem_{frame_id}"
        xml_element_tag = "paragraph"
        
        # Use IDMLPackage's method to create story properly
        self.idml.add_story_with_content(story_id, xml_element_id, xml_element_tag)
        
        # Step 4: Get story and set content
        story_name = f"Stories/Story_{story_id}.xml"
        story = Story(self.idml, story_name, self.working_copy_path)
        
        # Step 5: Set text content using Story's method
        story.set_element_content(xml_element_id, text_content)
        story.synchronize()
        
        return textframe, story
    
    def save(self):
        """
        Save all changes to the spread.
        """
        self.spread.synchronize()


def test_using_helper_class():
    """
    Demonstrate using the TextRangeBuilder helper class.
    
    This shows a clean pattern for working with simple_idml API.
    """
    test_idml = os.path.join(os.path.dirname(__file__), 'test', 'blank.idml')
    temp_dir = tempfile.mkdtemp()
    output_idml = os.path.join(temp_dir, 'output_with_builder.idml')
    
    try:
        print("\n" + "="*60)
        print("Test: Using TextRangeBuilder Helper Class")
        print("="*60)
        
        # Setup IDML package with working copy
        idml = IDMLPackage(test_idml, mode='r')
        working_copy_path = os.path.join(temp_dir, 'working_copy')
        os.makedirs(working_copy_path, exist_ok=True)
        idml.extractall(working_copy_path)
        idml.close()
        
        idml = IDMLPackage(test_idml, mode='r')
        idml.working_copy_path = working_copy_path
        
        # Get first spread using IDMLPackage.spreads_objects property
        spread = idml.spreads_objects[0]
        page = spread.pages[0]  # Using Spread.pages property
        
        print(f"Working with spread: {spread.name}")
        print(f"Page coordinates: {page.coordinates}")
        
        # Initialize builder
        builder = TextRangeBuilder(idml, spread)
        
        # Add text ranges using the builder
        text_ranges = [
            {
                'frame_id': 'frame_header',
                'story_id': 'story_header',
                'text': 'Document Header - Created with simple_idml',
                'x': 50,
                'y': -300,
                'width': 450,
                'height': 40
            },
            {
                'frame_id': 'frame_body',
                'story_id': 'story_body',
                'text': 'This is the main body text. The TextRangeBuilder class demonstrates clean usage of simple_idml API methods.',
                'x': 50,
                'y': -200,
                'width': 450,
                'height': 150
            },
            {
                'frame_id': 'frame_footer',
                'story_id': 'story_footer',
                'text': 'Page Footer',
                'x': 50,
                'y': 250,
                'width': 450,
                'height': 30
            }
        ]
        
        for tr in text_ranges:
            print(f"\nAdding text range: {tr['frame_id']}")
            print(f"  Text: {tr['text'][:50]}...")
            
            # Use the builder's add_text_range method
            textframe, story = builder.add_text_range(
                frame_id=tr['frame_id'],
                story_id=tr['story_id'],
                text_content=tr['text'],
                x=tr['x'],
                y=tr['y'],
                width=tr['width'],
                height=tr['height']
            )
            
            print(f"  ✓ Added TextFrame and Story")
        
        # Save all changes
        builder.save()
        idml.save(output_idml)
        
        print(f"\n✓ Saved to: {output_idml}")
        
        # Verify
        verify_idml = IDMLPackage(output_idml, mode='r')
        print(f"✓ Verification: {len(text_ranges)} stories found in output")
        
        for tr in text_ranges:
            if tr['story_id'] in verify_idml.story_ids:
                print(f"  ✓ Story '{tr['story_id']}' found")
            else:
                print(f"  ✗ Story '{tr['story_id']}' NOT found")
        
        verify_idml.close()
        return True
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_page_positioning():
    """
    Test different positioning strategies using Page properties.
    
    Demonstrates using Page.coordinates and Page.geometric_bounds
    for smart positioning of text ranges.
    """
    test_idml = os.path.join(os.path.dirname(__file__), 'test', 'blank.idml')
    temp_dir = tempfile.mkdtemp()
    output_idml = os.path.join(temp_dir, 'output_positioned.idml')
    
    try:
        print("\n" + "="*60)
        print("Test: Smart Positioning Using Page Properties")
        print("="*60)
        
        # Setup
        idml = IDMLPackage(test_idml, mode='r')
        working_copy_path = os.path.join(temp_dir, 'working_copy')
        os.makedirs(working_copy_path, exist_ok=True)
        idml.extractall(working_copy_path)
        idml.close()
        
        idml = IDMLPackage(test_idml, mode='r')
        idml.working_copy_path = working_copy_path
        
        spread = idml.spreads_objects[0]
        page = spread.pages[0]
        
        # Get page dimensions using Page properties
        page_width = page.coordinates['x2'] - page.coordinates['x1']
        page_height = page.coordinates['y2'] - page.coordinates['y1']
        
        print(f"Page dimensions: {page_width} x {page_height}")
        print(f"Page face: {page.face}")
        print(f"Is recto: {page.is_recto}")
        
        # Calculate positions based on page layout
        margin = Decimal('50')
        frame_width = Decimal('200')
        frame_height = Decimal('80')
        
        positions = {
            'top_left': (
                page.coordinates['x1'] + margin,
                page.coordinates['y1'] + margin
            ),
            'top_right': (
                page.coordinates['x2'] - frame_width - margin,
                page.coordinates['y1'] + margin
            ),
            'center': (
                page.coordinates['x1'] + (page_width - frame_width) / 2,
                page.coordinates['y1'] + (page_height - frame_height) / 2
            ),
            'bottom_left': (
                page.coordinates['x1'] + margin,
                page.coordinates['y2'] - frame_height - margin
            ),
            'bottom_right': (
                page.coordinates['x2'] - frame_width - margin,
                page.coordinates['y2'] - frame_height - margin
            ),
        }
        
        builder = TextRangeBuilder(idml, spread)
        
        for i, (position_name, (x, y)) in enumerate(positions.items()):
            frame_id = f"frame_{position_name}"
            story_id = f"story_{position_name}"
            text = f"Text at {position_name.replace('_', ' ').title()}"
            
            print(f"\nAdding frame at {position_name}: ({x}, {y})")
            
            builder.add_text_range(
                frame_id=frame_id,
                story_id=story_id,
                text_content=text,
                x=float(x),
                y=float(y),
                width=float(frame_width),
                height=float(frame_height)
            )
        
        builder.save()
        idml.save(output_idml)
        
        print(f"\n✓ Created IDML with {len(positions)} positioned text ranges")
        return True
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_accessing_existing_components():
    """
    Test accessing and modifying existing IDML components.
    
    Demonstrates using:
    - IDMLPackage.designmap for document structure
    - Spread properties and methods
    - Story properties and methods
    """
    test_idml = os.path.join(os.path.dirname(__file__), 'test', '2page.idml')
    
    if not os.path.exists(test_idml):
        print(f"Test file not found: {test_idml}")
        return False
    
    try:
        print("\n" + "="*60)
        print("Test: Accessing Existing IDML Components")
        print("="*60)
        
        idml = IDMLPackage(test_idml, mode='r')
        
        # Access designmap properties
        print(f"\nDesignmap properties:")
        print(f"  Active layer: {idml.designmap.active_layer}")
        print(f"  Number of layers: {len(idml.designmap.layer_nodes)}")
        print(f"  Number of spreads: {len(idml.spreads_objects)}")
        
        # Access spread properties
        for i, spread in enumerate(idml.spreads_objects):
            print(f"\nSpread {i+1}: {spread.name}")
            print(f"  Number of pages: {len(spread.pages)}")
            
            # Access page properties
            for j, page in enumerate(spread.pages):
                print(f"  Page {j+1}:")
                print(f"    Face: {page.face}")
                print(f"    Is recto: {page.is_recto}")
                print(f"    Coordinates: {page.coordinates}")
                print(f"    Page items count: {len(page.page_items)}")
        
        # Access stories
        print(f"\nStories:")
        print(f"  Total stories: {len(idml.stories)}")
        print(f"  Story IDs: {idml.story_ids}")
        
        # Access tags
        print(f"\nTags:")
        for tag in idml.tags:
            print(f"  {tag.get('Name')}: {tag.get('Self')}")
        
        idml.close()
        return True
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("="*60)
    print("Advanced Tests: TextRange Management with Simple IDML")
    print("="*60)
    
    tests = [
        ("TextRangeBuilder Helper Class", test_using_helper_class),
        ("Smart Page Positioning", test_page_positioning),
        ("Accessing Existing Components", test_accessing_existing_components),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*60)
    print("Test Summary:")
    print("="*60)
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    print("="*60)
    
    all_passed = all(r for _, r in results)
    sys.exit(0 if all_passed else 1)
