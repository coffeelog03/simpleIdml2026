# -*- coding: utf-8 -*-

"""
Test file for adding text ranges to spread->page structure
Using existing classes and methods from simple_idml.idml and simple_idml.components
"""

import os
import sys
import tempfile
import shutil
from lxml import etree

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simple_idml.idml import IDMLPackage
from simple_idml.components import Spread, Story, XMLElement


def test_add_text_range_to_page():
    """
    Test adding a text range (TextFrame) to a page in a spread.
    
    This test demonstrates:
    1. Opening an IDML package
    2. Accessing a spread
    3. Accessing pages in the spread
    4. Adding a TextFrame element (text range) to a page
    5. Creating story content for the TextFrame
    6. Saving the modified IDML
    """
    
    # Path to test IDML file
    test_idml = os.path.join(os.path.dirname(__file__), 'test', 'blank.idml')
    
    if not os.path.exists(test_idml):
        print(f"Test file not found: {test_idml}")
        return False
    
    # Create a temporary directory for working
    temp_dir = tempfile.mkdtemp()
    output_idml = os.path.join(temp_dir, 'output_with_text.idml')
    
    try:
        # Open IDML package in write mode
        print(f"Opening IDML file: {test_idml}")
        idml = IDMLPackage(test_idml, mode='r')
        
        # Extract to working copy
        working_copy_path = os.path.join(temp_dir, 'working_copy')
        os.makedirs(working_copy_path, exist_ok=True)
        
        # Extract all files
        idml.extractall(working_copy_path)
        idml.close()
        
        # Re-open with working copy
        idml = IDMLPackage(test_idml, mode='r')
        idml.working_copy_path = working_copy_path
        
        print(f"Number of spreads: {len(idml.spreads)}")
        print(f"Spreads: {idml.spreads}")
        
        # Get the first spread
        if not idml.spreads_objects:
            print("No spreads found in IDML")
            return False
        
        spread = idml.spreads_objects[0]
        print(f"\nSpread name: {spread.name}")
        print(f"Number of pages in spread: {len(spread.pages)}")
        
        # Get the first page
        if not spread.pages:
            print("No pages found in spread")
            return False
        
        page = spread.pages[0]
        print(f"Page geometric bounds: {page.geometric_bounds}")
        print(f"Page coordinates: {page.coordinates}")
        print(f"Page face: {page.face}")
        
        # Create a TextFrame element (text range)
        # TextFrame needs: Self, ParentStory, ItemTransform, GeometricBounds
        text_frame_id = "test_textframe_001"
        story_id = "test_story_001"
        
        # Position the TextFrame in the center of the page
        page_width = page.coordinates['x2'] - page.coordinates['x1']
        page_height = page.coordinates['y2'] - page.coordinates['y1']
        
        # TextFrame dimensions (in points)
        tf_width = 200
        tf_height = 100
        
        # Center position
        tf_x = page.coordinates['x1'] + (page_width - tf_width) / 2
        tf_y = page.coordinates['y1'] + (page_height - tf_height) / 2
        
        print(f"\nCreating TextFrame at position: ({tf_x}, {tf_y})")
        print(f"TextFrame dimensions: {tf_width} x {tf_height}")
        
        # Create TextFrame XML element
        textframe_xml = f"""
        <TextFrame Self="{text_frame_id}" 
                   ParentStory="{story_id}" 
                   ContentType="TextType"
                   ItemTransform="1 0 0 1 {tf_x} {tf_y}"
                   PreviousTextFrame="n"
                   NextTextFrame="n"
                   ItemLayer="{idml.designmap.active_layer}">
            <Properties>
                <PathGeometry>
                    <GeometryPathType PathOpen="false">
                        <PathPointArray>
                            <PathPointType Anchor="0 0" 
                                         LeftDirection="0 0" 
                                         RightDirection="0 0"/>
                            <PathPointType Anchor="{tf_width} 0" 
                                         LeftDirection="{tf_width} 0" 
                                         RightDirection="{tf_width} 0"/>
                            <PathPointType Anchor="{tf_width} {tf_height}" 
                                         LeftDirection="{tf_width} {tf_height}" 
                                         RightDirection="{tf_width} {tf_height}"/>
                            <PathPointType Anchor="0 {tf_height}" 
                                         LeftDirection="0 {tf_height}" 
                                         RightDirection="0 {tf_height}"/>
                        </PathPointArray>
                    </GeometryPathType>
                </PathGeometry>
            </Properties>
            <TextFramePreference TextColumnCount="1" TextColumnMaxWidth="0"/>
        </TextFrame>
        """
        
        textframe_element = etree.fromstring(textframe_xml)
        
        # Add TextFrame to spread
        spread.node.append(textframe_element)
        
        print(f"TextFrame added to spread")
        
        # Create a Story for the TextFrame content
        xml_element_id = "test_xmlelement_001"
        xml_element_tag = "test_paragraph"
        
        # Add the story to the package
        print(f"Creating story: {story_id}")
        idml.add_story_with_content(story_id, xml_element_id, xml_element_tag)
        
        # Get the story and add text content
        story_name = f"Stories/Story_{story_id}.xml"
        story = Story(idml, story_name, working_copy_path)
        
        # Add text content to the XMLElement
        text_content = "Hello from simple_idml! This is a test text range."
        print(f"Adding text content: '{text_content}'")
        
        story.set_element_content(xml_element_id, text_content)
        story.synchronize()
        
        # Synchronize the spread
        spread.synchronize()
        
        print("\nChanges synchronized")
        
        # Save the modified IDML
        print(f"Saving to: {output_idml}")
        idml.save(output_idml)
        
        # Verify the output file exists
        if os.path.exists(output_idml):
            print(f"✓ Success! Output file created: {output_idml}")
            print(f"  File size: {os.path.getsize(output_idml)} bytes")
            
            # Verify the content
            verify_idml = IDMLPackage(output_idml, mode='r')
            verify_spread = verify_idml.spreads_objects[0]
            
            # Check if TextFrame was added
            textframes = verify_spread.dom.xpath(f"//TextFrame[@Self='{text_frame_id}']")
            if textframes:
                print(f"✓ TextFrame found in output IDML")
            else:
                print(f"✗ TextFrame not found in output IDML")
            
            # Check if Story was added
            if story_id in verify_idml.story_ids:
                print(f"✓ Story found in output IDML")
            else:
                print(f"✗ Story not found in output IDML")
            
            verify_idml.close()
            return True
        else:
            print(f"✗ Failed to create output file")
            return False
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\nCleaned up temporary directory: {temp_dir}")


def test_add_multiple_text_ranges():
    """
    Test adding multiple text ranges to demonstrate the pattern.
    """
    test_idml = os.path.join(os.path.dirname(__file__), 'test', 'blank.idml')
    
    if not os.path.exists(test_idml):
        print(f"Test file not found: {test_idml}")
        return False
    
    temp_dir = tempfile.mkdtemp()
    output_idml = os.path.join(temp_dir, 'output_multiple_text.idml')
    
    try:
        print(f"\n{'='*60}")
        print("Test: Adding Multiple Text Ranges")
        print(f"{'='*60}")
        
        # Open and prepare IDML
        idml = IDMLPackage(test_idml, mode='r')
        working_copy_path = os.path.join(temp_dir, 'working_copy')
        os.makedirs(working_copy_path, exist_ok=True)
        idml.extractall(working_copy_path)
        idml.close()
        
        idml = IDMLPackage(test_idml, mode='r')
        idml.working_copy_path = working_copy_path
        
        spread = idml.spreads_objects[0]
        page = spread.pages[0]
        
        # Add 3 text frames at different positions
        text_data = [
            ("tf001", "story001", "Hello Top", 100, 50),
            ("tf002", "story002", "Hello Middle", 100, 200),
            ("tf003", "story003", "Hello Bottom", 100, 350),
        ]
        
        for tf_id, story_id, text, y_pos, x_pos in text_data:
            print(f"\nAdding TextFrame '{tf_id}' with text: '{text}'")
            
            # Create TextFrame
            textframe_xml = f"""
            <TextFrame Self="{tf_id}" 
                       ParentStory="{story_id}" 
                       ContentType="TextType"
                       ItemTransform="1 0 0 1 {x_pos} {y_pos}"
                       PreviousTextFrame="n"
                       NextTextFrame="n"
                       ItemLayer="{idml.designmap.active_layer}">
                <Properties>
                    <PathGeometry>
                        <GeometryPathType PathOpen="false">
                            <PathPointArray>
                                <PathPointType Anchor="0 0" LeftDirection="0 0" RightDirection="0 0"/>
                                <PathPointType Anchor="200 0" LeftDirection="200 0" RightDirection="200 0"/>
                                <PathPointType Anchor="200 50" LeftDirection="200 50" RightDirection="200 50"/>
                                <PathPointType Anchor="0 50" LeftDirection="0 50" RightDirection="0 50"/>
                            </PathPointArray>
                        </GeometryPathType>
                    </PathGeometry>
                </Properties>
                <TextFramePreference TextColumnCount="1" TextColumnMaxWidth="0"/>
            </TextFrame>
            """
            
            textframe_element = etree.fromstring(textframe_xml)
            spread.node.append(textframe_element)
            
            # Create story and add content
            xml_elem_id = f"xmlelem_{tf_id}"
            idml.add_story_with_content(story_id, xml_elem_id, "paragraph")
            
            story = Story(idml, f"Stories/Story_{story_id}.xml", working_copy_path)
            story.set_element_content(xml_elem_id, text)
            story.synchronize()
        
        # Save all changes
        spread.synchronize()
        idml.save(output_idml)
        
        if os.path.exists(output_idml):
            print(f"\n✓ Success! Created IDML with {len(text_data)} text ranges")
            print(f"  Output: {output_idml}")
            return True
        else:
            print(f"\n✗ Failed to create output file")
            return False
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    print("="*60)
    print("Testing: Add TextRange to Spread->Page")
    print("="*60)
    
    # Run basic test
    result1 = test_add_text_range_to_page()
    
    # Run multiple text ranges test
    result2 = test_add_multiple_text_ranges()
    
    print("\n" + "="*60)
    print("Test Results:")
    print(f"  Single TextRange Test: {'PASSED' if result1 else 'FAILED'}")
    print(f"  Multiple TextRanges Test: {'PASSED' if result2 else 'FAILED'}")
    print("="*60)
    
    sys.exit(0 if (result1 and result2) else 1)
