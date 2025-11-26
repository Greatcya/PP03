


import pytest
from PIL import Image
import os
import json
from processing import ImageProcessor

def test_load_image():

    processor = ImageProcessor()
    
    test_path = 'test_load.png'
    test_img = Image.new('RGB', (100, 100), color='red')
    test_img.save(test_path)
    test_img.close()  
    
    try:
        
        loaded = processor.load(test_path)
        
        assert loaded is not None
        assert loaded.size == (100, 100)
        assert loaded.mode == 'RGB'
        loaded.close()  
        
    finally:
        
        if os.path.exists(test_path):
            os.remove(test_path)

def test_load_nonexistent():

    processor = ImageProcessor()
    
    with pytest.raises(FileNotFoundError):
        processor.load('nonexistent_file.jpg')

def test_get_info():

    processor = ImageProcessor()
    
    test_img = Image.new('RGB', (200, 150))
    
    info = processor.get_info(test_img)
    
    assert info['w'] == 200
    assert info['h'] == 150
    assert info['mode'] == 'RGB'
    
    test_img.close()

def test_transform_resize():

    processor = ImageProcessor()
    
    original = Image.new('RGB', (100, 100))
    
    resized = processor.transform(original, (50, 50), False, False)
    
    assert resized.size == (50, 50)
    
    original.close()
    resized.close()

def test_transform_filters():

    processor = ImageProcessor()
    
    original = Image.new('RGB', (100, 100))
    
    sharpened = processor.transform(original, None, True, False)
    contoured = processor.transform(original, None, False, True)
    both_filters = processor.transform(original, None, True, True)
    
    assert sharpened is not None
    assert contoured is not None
    assert both_filters is not None

    original.close()
    sharpened.close()
    contoured.close()
    both_filters.close()

def test_save_image():

    processor = ImageProcessor()
    
    test_img = Image.new('RGB', (50, 50))
    save_path = 'test_save_output.jpg'
    
    try:
        
        processor.save(test_img, save_path)
        
        assert os.path.exists(save_path)
        
    finally:
        test_img.close()
        
        import time
        time.sleep(0.1)
        if os.path.exists(save_path):
            os.remove(save_path)

def test_log_action():
    processor = ImageProcessor()
    log_file = 'test_forge_history.json'
    
    original_file = processor.history_file
    processor.history_file = log_file
    
    try:
        
        processor.log_action('test_action', {'param': 'value'})
        
        assert os.path.exists(log_file)
        
        with open(log_file, 'r', encoding='utf-8') as f:
            history = json.load(f) 
        assert len(history) > 0
        assert history[-1]['action'] == 'test_action'
        
    finally:

        processor.history_file = original_file
        if os.path.exists(log_file):
            os.remove(log_file)


def test_transform_no_resize():

    processor = ImageProcessor()
    
    original = Image.new('RGB', (80, 60))
    
    
    result = processor.transform(original, None, False, False)
    
    assert result.size == (80, 60)
    
    original.close()
    result.close()

# в папку с main.py и "pytest test_processing.py" -v в консоль