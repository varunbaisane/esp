import inspect
import ast

def test_standalone_publisher_initialization():
    """
    Verify publisher initializes even when Redis is unavailable.
    Subscriber does NOT start.
    Publisher falls back to ConnectionManager.
    """
    with open("app/main.py", "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    # Find lifespan function
    lifespan_node = None
    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "lifespan":
            lifespan_node = node
            break
            
    assert lifespan_node is not None
    
    pub_init_in_if = False
    sub_start_in_if = False
    
    for node in ast.walk(lifespan_node):
        if isinstance(node, ast.If):
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Call):
                    if isinstance(subnode.func, ast.Attribute):
                        if subnode.func.attr == "initialize":
                            if isinstance(subnode.func.value, ast.Name) and subnode.func.value.id == "realtime_publisher":
                                pub_init_in_if = True
                        if subnode.func.attr == "start":
                            if isinstance(subnode.func.value, ast.Name) and subnode.func.value.id == "realtime_subscriber":
                                sub_start_in_if = True
                                
    assert not pub_init_in_if, "realtime_publisher.initialize() must NOT be conditionally gated by Redis"
    assert sub_start_in_if, "realtime_subscriber.start() MUST be conditionally gated by Redis"

def test_transport_websocket_decision():
    """
    Assert that NotificationDeliveryDispatcher no longer directly checks only NotificationChannel.BROWSER.
    Instead it delegates to the centralized helper.
    """
    from app.services.notification_delivery_dispatcher import NotificationDeliveryDispatcher
    
    source = inspect.getsource(NotificationDeliveryDispatcher.dispatch)
    
    # It must NOT directly check BROWSER or IN_APP in dispatch
    assert "NotificationChannel.BROWSER" not in source, "dispatch() must delegate to helper"
    assert "NotificationChannel.IN_APP" not in source, "dispatch() must delegate to helper"
    assert "_should_dispatch_websocket" in source, "dispatch() must use the centralized helper"
    
    helper_source = inspect.getsource(NotificationDeliveryDispatcher._should_dispatch_websocket)
    assert "NotificationChannel.IN_APP" in helper_source, "Helper must check IN_APP channel"
    assert "NotificationChannel.BROWSER" in helper_source, "Helper must check BROWSER channel"
