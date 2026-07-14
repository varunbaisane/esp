import ast
import inspect

def test_google_auth_service_layering():
    """
    Ensure GoogleAuthService never imports Repository, JWT, Redis, WebSocket, Notification.
    It should only verify tokens.
    """
    import app.services.google_auth_service as gas
    source = inspect.getsource(gas)
    
    tree = ast.parse(source)
    
    forbidden_terms = ["Repository", "JWT", "Redis", "WebSocket", "Notification"]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for term in forbidden_terms:
                    assert term.lower() not in alias.name.lower(), f"GoogleAuthService must not import {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for term in forbidden_terms:
                    assert term.lower() not in node.module.lower(), f"GoogleAuthService must not import from {node.module}"
            for alias in node.names:
                for term in forbidden_terms:
                    assert term.lower() not in alias.name.lower(), f"GoogleAuthService must not import {alias.name}"
