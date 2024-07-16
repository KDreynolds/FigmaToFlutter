import os
from dotenv import load_dotenv
import requests
import json
from typing import Dict, List, Any

load_dotenv()

class FigmaClient:
    BASE_URL = "https://api.figma.com/v1"

    def __init__(self):
        self.headers = {
            "X-Figma-Token": os.getenv("PERSONAL_ACCESS_TOKEN")
        }
        self.file_key = os.getenv("FILE_KEY")

    def get_file(self, file_key: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/files/{file_key}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch file: {response.status_code}")

    def get_file_nodes(self, file_key: str, node_ids: List[str]) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/files/{file_key}/nodes"
        params = {"ids": ",".join(node_ids)}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch nodes: {response.status_code}")

class FigmaParser:
    def __init__(self, figma_data: Dict[str, Any]):
        self.figma_data = figma_data

    def parse_document(self) -> Dict[str, Any]:
        document = self.figma_data.get('document')
        if not document:
            return {'error': 'No document found in Figma data'}
        
        return self.parse_node(document)

    def parse_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        node_type = node['type']
        if node_type == 'CANVAS':
            return self.parse_canvas(node)
        elif node_type == 'FRAME' or node_type == 'GROUP':
            return self.parse_frame(node)
        elif node_type == 'TEXT':
            return self.parse_text(node)
        elif node_type == 'RECTANGLE':
            return self.parse_rectangle(node)
        else:
            return {'type': 'unsupported', 'original_type': node_type}

    def parse_canvas(self, canvas: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'canvas',
            'name': canvas['name'],
            'children': [self.parse_node(child) for child in canvas['children']]
        }

    def parse_frame(self, frame: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'container',
            'name': frame['name'],
            'width': frame['absoluteBoundingBox']['width'],
            'height': frame['absoluteBoundingBox']['height'],
            'children': [self.parse_node(child) for child in frame['children']]
        }

    def parse_text(self, text: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'text',
            'name': text['name'],
            'characters': text['characters'],
            'style': {
                'fontSize': text['style'].get('fontSize'),
                'fontWeight': text['style'].get('fontWeight'),
                'textAlignHorizontal': text['style'].get('textAlignHorizontal'),
                'textAlignVertical': text['style'].get('textAlignVertical'),
            }
        }

    def parse_rectangle(self, rectangle: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'rectangle',
            'name': rectangle['name'],
            'width': rectangle['absoluteBoundingBox']['width'],
            'height': rectangle['absoluteBoundingBox']['height'],
            'cornerRadius': rectangle.get('cornerRadius', 0),
            'fills': rectangle.get('fills', [])
        }

class FlutterCodeGenerator:
    def generate_widget(self, node: Dict[str, Any], indent: int = 0) -> str:
        node_type = node['type']
        if node_type == 'container':
            return self.generate_container(node, indent)
        elif node_type == 'text':
            return self.generate_text(node, indent)
        elif node_type == 'rectangle':
            return self.generate_rectangle(node, indent)
        else:
            return ' ' * indent + f"// Unsupported type: {node_type}"

    def generate_container(self, node: Dict[str, Any], indent: int) -> str:
        children = '\n'.join([self.generate_widget(child, indent + 2) for child in node['children']])
        return f"""
{' ' * indent}Container(
{' ' * (indent + 2)}width: {node['width']},
{' ' * (indent + 2)}height: {node['height']},
{' ' * (indent + 2)}child: Column(
{' ' * (indent + 4)}children: [
{children}
{' ' * (indent + 4)}],
{' ' * (indent + 2)}),
{' ' * indent})"""

    def generate_text(self, node: Dict[str, Any], indent: int) -> str:
        style = node['style']
        return f"""
{' ' * indent}Text(
{' ' * (indent + 2)}'{node['characters']}',
{' ' * (indent + 2)}style: TextStyle(
{' ' * (indent + 4)}fontSize: {style['fontSize']},
{' ' * (indent + 4)}fontWeight: FontWeight.w{style['fontWeight']},
{' ' * (indent + 2)}),
{' ' * indent})"""

    def generate_rectangle(self, node: Dict[str, Any], indent: int) -> str:
        return f"""
{' ' * indent}Container(
{' ' * (indent + 2)}width: {node['width']},
{' ' * (indent + 2)}height: {node['height']},
{' ' * (indent + 2)}decoration: BoxDecoration(
{' ' * (indent + 4)}color: Color(0xFF{node['fills'][0]['color']['r']:02X}{node['fills'][0]['color']['g']:02X}{node['fills'][0]['color']['b']:02X}),
{' ' * (indent + 4)}borderRadius: BorderRadius.circular({node['cornerRadius']}),
{' ' * (indent + 2)}),
{' ' * indent})"""

if __name__ == "__main__":
    client = FigmaClient()
    file_data = client.get_file(client.file_key)

    parser = FigmaParser(file_data)
    parsed_data = parser.parse_document()

    print("Parsed Data Structure:")
    print(json.dumps(parsed_data, indent=2))

    code_generator = FlutterCodeGenerator()

    # Check if 'children' exists in parsed_data
    if 'children' in parsed_data and parsed_data['children']:
        flutter_code = code_generator.generate_widget(parsed_data['children'][0])
        print("\nGenerated Flutter Code:")
        print(flutter_code)
    else:
        print("\nNo 'children' found in the parsed data or it's empty.")
        print("Here's the structure of parsed_data:")
        print(json.dumps(parsed_data, indent=2))