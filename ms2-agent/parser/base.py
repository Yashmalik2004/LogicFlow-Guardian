from abc import ABC, abstractmethod

class BaseParser(ABC):
    """
    Abstract base class for all language-specific parsers.
    
    Every new language parser (e.g., Python, JavaScript, Go) must inherit 
    from this class and implement the `parse` method.
    """
    
    @abstractmethod
    def parse(self, file_path: str, content: str) -> dict:
        """
        Parse the content of a source file and return a dictionary of 
        extracted AST-level elements.
        
        Parameters
        ----------
        file_path : str
            Absolute or relative path to the source file (used for context/logging).
        content : str
            UTF-8 decoded source code content of the file.
            
        Returns
        -------
        dict
            Normalized structure containing:
            {
                "imports": list[dict],
                "exports": list[dict],
                "classes": list[dict],
                "functions": list[dict],
                "routes": list[dict],
                "middleware": list[dict]
            }
        """
        pass
