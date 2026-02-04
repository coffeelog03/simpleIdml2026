# -*- coding: utf-8 -*-

"""
Test file for saving IDML output to a fixed directory for InDesign inspection.

This version saves the output files to /home/user/webapp/output/ directory
so you can open them in InDesign.
"""

import os
import sys
import shutil
from lxml import etree

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simple_idml.idml import IDMLPackage
from simple_idml.components import Spread, Story, XMLElement


def create_output_directory():
    """Create output directory for saving IDML files."""
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def test_save_single_text_range():
    """
    Create IDML with single text range and save to output directory.
    """
    test_idml = os.path.join(os.path.dirname(__file__), 'test', 'blank.idml')
    
    if not os.path.exists(test_idml):
        print(f"Test file not found: {test_idml}")
        return None
    
    # Create output directory
    output_dir = create_output_directory()
    output_idml = os.path.join(output_dir, 'single_text_range.idml')
    working_copy = os.path.join(output_dir, 'working_single')
    
    # Clean up working copy if exists
    if os.path.exists(working_copy):
        shutil.rmtree(working_copy)
    
    try:
        print("\n" + "="*60)
        print("Creating IDML with Single Text Range")
        print("="*60)
        
        # Open IDML
        idml = IDMLPackage(test_idml, mode='r')
        
        # Extract to working copy
        os.makedirs(working_copy, exist_ok=True)
        idml.extractall(working_copy)
        idml.close()
        
        # Re-open with working copy
        idml = IDMLPackage(test_idml, mode='r')
        idml.working_copy_path = working_copy
        
        # Get spread and page
        spread = idml.spreads_objects[0]
        page = spread.pages[0]
        
        print(f"Page coordinates: {page.coordinates}")
        
        # Calculate center position
        page_width = page.coordinates['x2'] - page.coordinates['x1']
        page_height = page.coordinates['y2'] - page.coordinates['y1']
        
        frame_width = 300
        frame_height = 150
        
        center_x = page.coordinates['x1'] + (page_width - frame_width) / 2
        center_y = page.coordinates['y1'] + (page_height - frame_height) / 2
        
        # Create TextFrame
        frame_id = "textframe_center"
        story_id = "story_center"
        
        textframe_xml = f"""
        <TextFrame Self="{frame_id}" 
                   ParentStory="{story_id}" 
                   ContentType="TextType"
                   ItemTransform="1 0 0 1 {center_x} {center_y}"
                   PreviousTextFrame="n"
                   NextTextFrame="n"
                   ItemLayer="{idml.designmap.active_layer}">
            <Properties>
                <PathGeometry>
                    <GeometryPathType PathOpen="false">
                        <PathPointArray>
                            <PathPointType Anchor="0 0" LeftDirection="0 0" RightDirection="0 0"/>
                            <PathPointType Anchor="{frame_width} 0" LeftDirection="{frame_width} 0" RightDirection="{frame_width} 0"/>
                            <PathPointType Anchor="{frame_width} {frame_height}" LeftDirection="{frame_width} {frame_height}" RightDirection="{frame_width} {frame_height}"/>
                            <PathPointType Anchor="0 {frame_height}" LeftDirection="0 {frame_height}" RightDirection="0 {frame_height}"/>
                        </PathPointArray>
                    </GeometryPathType>
                </PathGeometry>
            </Properties>
            <TextFramePreference TextColumnCount="1" TextColumnMaxWidth="0"/>
        </TextFrame>
        """
        
        textframe = etree.fromstring(textframe_xml)
        spread.node.append(textframe)
        
        # Create story
        xml_element_id = "xmlelem_center"
        idml.add_story_with_content(story_id, xml_element_id, "paragraph")
        
        story = Story(idml, f"Stories/Story_{story_id}.xml", working_copy)
        text_content = "Hello from simple_idml!\n\nThis text was created programmatically.\n\nYou can now open this IDML file in Adobe InDesign."
        story.set_element_content(xml_element_id, text_content)
        story.synchronize()
        
        # Save changes
        spread.synchronize()
        idml.save(output_idml)
        
        print(f"\n✅ IDML created successfully!")
        print(f"📁 Output file: {output_idml}")
        print(f"📐 Position: ({center_x:.2f}, {center_y:.2f})")
        print(f"📏 Size: {frame_width} x {frame_height}")
        
        return output_idml
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_save_multiple_text_ranges():
    """
    Create IDML with multiple text ranges at different positions.
    """
    test_idml = os.path.join(os.path.dirname(__file__), 'test', 'blank.idml')
    
    if not os.path.exists(test_idml):
        print(f"Test file not found: {test_idml}")
        return None
    
    # Create output directory
    output_dir = create_output_directory()
    output_idml = os.path.join(output_dir, 'multiple_text_ranges.idml')
    working_copy = os.path.join(output_dir, 'working_multiple')
    
    # Clean up working copy if exists
    if os.path.exists(working_copy):
        shutil.rmtree(working_copy)
    
    try:
        print("\n" + "="*60)
        print("Creating IDML with Multiple Text Ranges")
        print("="*60)
        
        # Setup
        idml = IDMLPackage(test_idml, mode='r')
        os.makedirs(working_copy, exist_ok=True)
        idml.extractall(working_copy)
        idml.close()
        
        idml = IDMLPackage(test_idml, mode='r')
        idml.working_copy_path = working_copy
        
        spread = idml.spreads_objects[0]
        page = spread.pages[0]
        
        # Define text ranges with positions and content
        text_ranges = [
            {
                'id': 'header',
                'x': 50,
                'y': -300,
                'width': 450,
                'height': 50,
                'text': '📄 DOCUMENT HEADER\n\nCreated with simple_idml Python library'
            },
            {
                'id': 'body_left',
                'x': 50,
                'y': -200,
                'width': 200,
                'height': 300,
                'text': 'Left Column\n\nThis is the left column of text. It demonstrates multi-column layout capabilities.'
            },
            {
                'id': 'body_right',
                'x': 270,
                'y': -200,
                'width': 230,
                'height': 300,
                'text': 'Right Column\n\nThis is the right column. You can position text frames anywhere on the page.'
            },
            {
                'id': 'footer',
                'x': 50,
                'y': 250,
                'width': 450,
                'height': 40,
                'text': 'Page Footer - Generated automatically'
            }
        ]
        
        for tr in text_ranges:
            print(f"\nAdding text range: {tr['id']}")
            print(f"  Position: ({tr['x']}, {tr['y']})")
            print(f"  Size: {tr['width']} x {tr['height']}")
            
            frame_id = f"frame_{tr['id']}"
            story_id = f"story_{tr['id']}"
            
            # Create TextFrame
            textframe_xml = f"""
            <TextFrame Self="{frame_id}" 
                       ParentStory="{story_id}" 
                       ContentType="TextType"
                       ItemTransform="1 0 0 1 {tr['x']} {tr['y']}"
                       PreviousTextFrame="n"
                       NextTextFrame="n"
                       ItemLayer="{idml.designmap.active_layer}">
                <Properties>
                    <PathGeometry>
                        <GeometryPathType PathOpen="false">
                            <PathPointArray>
                                <PathPointType Anchor="0 0" LeftDirection="0 0" RightDirection="0 0"/>
                                <PathPointType Anchor="{tr['width']} 0" LeftDirection="{tr['width']} 0" RightDirection="{tr['width']} 0"/>
                                <PathPointType Anchor="{tr['width']} {tr['height']}" LeftDirection="{tr['width']} {tr['height']}" RightDirection="{tr['width']} {tr['height']}"/>
                                <PathPointType Anchor="0 {tr['height']}" LeftDirection="0 {tr['height']}" RightDirection="0 {tr['height']}"/>
                            </PathPointArray>
                        </GeometryPathType>
                    </PathGeometry>
                </Properties>
                <TextFramePreference TextColumnCount="1" TextColumnMaxWidth="0"/>
            </TextFrame>
            """
            
            textframe = etree.fromstring(textframe_xml)
            spread.node.append(textframe)
            
            # Create story
            xml_element_id = f"xmlelem_{tr['id']}"
            idml.add_story_with_content(story_id, xml_element_id, "paragraph")
            
            story = Story(idml, f"Stories/Story_{story_id}.xml", working_copy)
            story.set_element_content(xml_element_id, tr['text'])
            story.synchronize()
        
        # Save
        spread.synchronize()
        idml.save(output_idml)
        
        print(f"\n✅ IDML created successfully!")
        print(f"📁 Output file: {output_idml}")
        print(f"📊 Total text ranges: {len(text_ranges)}")
        
        return output_idml
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_save_positioned_layout():
    """
    Create IDML with text ranges positioned at all corners and center.
    """
    test_idml = os.path.join(os.path.dirname(__file__), 'test', 'blank.idml')
    
    if not os.path.exists(test_idml):
        print(f"Test file not found: {test_idml}")
        return None
    
    # Create output directory
    output_dir = create_output_directory()
    output_idml = os.path.join(output_dir, 'positioned_layout.idml')
    working_copy = os.path.join(output_dir, 'working_positioned')
    
    # Clean up working copy if exists
    if os.path.exists(working_copy):
        shutil.rmtree(working_copy)
    
    try:
        print("\n" + "="*60)
        print("Creating IDML with Positioned Layout")
        print("="*60)
        
        # Setup
        idml = IDMLPackage(test_idml, mode='r')
        os.makedirs(working_copy, exist_ok=True)
        idml.extractall(working_copy)
        idml.close()
        
        idml = IDMLPackage(test_idml, mode='r')
        idml.working_copy_path = working_copy
        
        spread = idml.spreads_objects[0]
        page = spread.pages[0]
        
        # Calculate positions
        margin = 30
        frame_width = 150
        frame_height = 80
        
        page_width = page.coordinates['x2'] - page.coordinates['x1']
        page_height = page.coordinates['y2'] - page.coordinates['y1']
        
        positions = {
            'top_left': {
                'x': float(page.coordinates['x1'] + margin),
                'y': float(page.coordinates['y1'] + margin),
                'text': '📍 Top Left\n\nPosition: Top Left Corner'
            },
            'top_right': {
                'x': float(page.coordinates['x2'] - frame_width - margin),
                'y': float(page.coordinates['y1'] + margin),
                'text': '📍 Top Right\n\nPosition: Top Right Corner'
            },
            'center': {
                'x': float(page.coordinates['x1'] + (page_width - frame_width) / 2),
                'y': float(page.coordinates['y1'] + (page_height - frame_height) / 2),
                'text': '📍 Center\n\nPosition: Page Center'
            },
            'bottom_left': {
                'x': float(page.coordinates['x1'] + margin),
                'y': float(page.coordinates['y2'] - frame_height - margin),
                'text': '📍 Bottom Left\n\nPosition: Bottom Left Corner'
            },
            'bottom_right': {
                'x': float(page.coordinates['x2'] - frame_width - margin),
                'y': float(page.coordinates['y2'] - frame_height - margin),
                'text': '📍 Bottom Right\n\nPosition: Bottom Right Corner'
            }
        }
        
        for pos_name, pos_data in positions.items():
            print(f"\nAdding frame at: {pos_name}")
            print(f"  Coordinates: ({pos_data['x']:.2f}, {pos_data['y']:.2f})")
            
            frame_id = f"frame_{pos_name}"
            story_id = f"story_{pos_name}"
            
            textframe_xml = f"""
            <TextFrame Self="{frame_id}" 
                       ParentStory="{story_id}" 
                       ContentType="TextType"
                       ItemTransform="1 0 0 1 {pos_data['x']} {pos_data['y']}"
                       PreviousTextFrame="n"
                       NextTextFrame="n"
                       ItemLayer="{idml.designmap.active_layer}">
                <Properties>
                    <PathGeometry>
                        <GeometryPathType PathOpen="false">
                            <PathPointArray>
                                <PathPointType Anchor="0 0" LeftDirection="0 0" RightDirection="0 0"/>
                                <PathPointType Anchor="{frame_width} 0" LeftDirection="{frame_width} 0" RightDirection="{frame_width} 0"/>
                                <PathPointType Anchor="{frame_width} {frame_height}" LeftDirection="{frame_width} {frame_height}" RightDirection="{frame_width} {frame_height}"/>
                                <PathPointType Anchor="0 {frame_height}" LeftDirection="0 {frame_height}" RightDirection="0 {frame_height}"/>
                            </PathPointArray>
                        </GeometryPathType>
                    </PathGeometry>
                </Properties>
                <TextFramePreference TextColumnCount="1" TextColumnMaxWidth="0"/>
            </TextFrame>
            """
            
            textframe = etree.fromstring(textframe_xml)
            spread.node.append(textframe)
            
            xml_element_id = f"xmlelem_{pos_name}"
            idml.add_story_with_content(story_id, xml_element_id, "paragraph")
            
            story = Story(idml, f"Stories/Story_{story_id}.xml", working_copy)
            story.set_element_content(xml_element_id, pos_data['text'])
            story.synchronize()
        
        # Save
        spread.synchronize()
        idml.save(output_idml)
        
        print(f"\n✅ IDML created successfully!")
        print(f"📁 Output file: {output_idml}")
        print(f"📊 Total positions: {len(positions)}")
        
        return output_idml
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    print("="*60)
    print("Creating IDML Files for InDesign Inspection")
    print("="*60)
    
    results = []
    
    # Test 1: Single text range
    output1 = test_save_single_text_range()
    if output1:
        results.append(('Single Text Range', output1))
    
    # Test 2: Multiple text ranges
    output2 = test_save_multiple_text_ranges()
    if output2:
        results.append(('Multiple Text Ranges', output2))
    
    # Test 3: Positioned layout
    output3 = test_save_positioned_layout()
    if output3:
        results.append(('Positioned Layout', output3))
    
    # Summary
    print("\n" + "="*60)
    print("Summary - Files Ready for InDesign")
    print("="*60)
    
    if results:
        print("\n✅ Successfully created IDML files:\n")
        for name, path in results:
            print(f"  📄 {name}")
            print(f"     {path}\n")
        
        print("📂 All files are in the 'output' directory")
        print("🔧 Open these files in Adobe InDesign to inspect the results")
    else:
        print("\n❌ No files were created")
    
    print("="*60)
