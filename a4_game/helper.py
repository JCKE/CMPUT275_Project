import math

def clamp(x, a, b):
    """
    Clamps x between the values of a and b, where a <= x <= b.
    Clever method shamelessly stolen from
    http://stackoverflow.com/questions/4092528/how-to-clamp-an-integer-to-some-
    range-in-python
    
    >>> clamp(10, 0, 5)
    5
    >>> clamp(-7, -5, 5)
    -5
    >>> clamp(3, -10, 10)
    3
    
    """
    return min(b, max(x, a))

def manhattan_dist(a, b):
    """
    Returns the Manhattan distance between two points.
    
    >>> manhattan_dist((0, 0), (5, 5))
    10
    >>> manhattan_dist((0, 5), (10, 7))
    12
    >>> manhattan_dist((12, 9), (2, 3))
    16
    >>> manhattan_dist((0, 5), (5, 0))
    10
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def squared_dist(a, b):
    """
    Returns the squared distance "as the crow flies" between two points.
    
    >>> squared_dist((0, 0), (5, 5)) == 50
    True
    >>> squared_dist((0, 5), (10, 7)) == 104
    True
    >>> squared_dist((12, 9), (2, 3)) == 136
    True
    """
    dx, dy = b[0] - a[0], b[1] - a[1]
    return dx * dx + dy * dy
    
def squared_segment_dist(p, a, b):
    """
    Returns the distance between a point p and a line segment between
    the points a and b.
    Code adapted from http://stackoverflow.com/questions/849211/shortest
    -distance-between-a-point-and-a-line-segment
    
    Examples:
    >>> squared_segment_dist((0, 2), (0, 0), (5, 5)) == 2
    True
    
    A point on the line has distance 0:
    >>> squared_segment_dist((3, 3), (0, 0), (5, 5)) == 0
    True
    
    If the point is beyond the beginning of the line, you will just
    get the squared distance from p to a:
    >>> squared_segment_dist((0, 1), (3, 2), (5, 9)) == squared_dist((0, 1), (3, 2))
    True
    
    The same applies for the end point:
    >>> squared_segment_dist((10, 15), (3, 2), (5, 9)) == squared_dist((10, 15), (5, 9))
    True
    """
    len2 = squared_dist(a, b)
    # If the segment is actually a point, our job is a lot easier!
    if len2 == 0: return squared_dist(p, a)
    # Our line is a + t * (b - a)
    # The t at which p is closest is when the vector (a, p) is projected
    # onto the vector (a, b) (dot product)
    t = ((p[0] - a[0]) * (b[0] - a[0]) 
        + (p[1] - a[1]) * (b[1] - a[1])) / len2
    if t < 0: return squared_dist(p, a) # Beyond point a
    if t > 1: return squared_dist(p, b) # Beyond point b
    close_point = (
        a[0] + t * (b[0] - a[0]),
        a[1] + t * (b[1] - a[1])
    )
    return squared_dist(p, close_point)
