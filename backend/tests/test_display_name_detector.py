from ai.display_name.display_name_detector import DisplayNameDetector

detector = DisplayNameDetector()

print(detector.detect("MacBook Pro"))
print(detector.detect("John Doe"))
print(detector.detect("Alice"))
print(detector.detect("Windows"))