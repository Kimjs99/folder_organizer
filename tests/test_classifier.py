import pytest
from pathlib import Path
from organizer.classifier import Classifier

@pytest.fixture
def config():
    return {
        "root": "~/Documents/정리함",
        "archive_before": 2024,
        "rules": [
            {
                "name": "01_학교업무/생기부·세특",
                "keywords": ["세특", "생기부"],
                "extensions": [".docx", ".hwp"]
            },
            {
                "name": "02_개발·IT/웹개발_프로젝트",
                "keywords": ["react", "component"],
                "extensions": [".jsx", ".tsx"]
            }
        ],
        "default_destination": "04_참고자료/다운로드_정리"
    }

def test_classifier_extensions(config, tmp_path):
    classifier = Classifier(config)
    
    file1 = tmp_path / "test.docx"
    file1.touch()
    
    dest = classifier.get_topic_folder(file1)
    assert dest == "01_학교업무/생기부·세특"
    
def test_classifier_keywords(config, tmp_path):
    classifier = Classifier(config)
    
    file2 = tmp_path / "세특_3학년.pdf"
    file2.touch()
    
    dest = classifier.get_topic_folder(file2)
    assert dest == "01_학교업무/생기부·세특"

def test_classifier_default(config, tmp_path):
    classifier = Classifier(config)
    
    file3 = tmp_path / "unknown.xyz"
    file3.touch()
    
    dest = classifier.get_topic_folder(file3)
    assert dest == "04_참고자료/다운로드_정리"
