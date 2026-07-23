def get_center_of_bbox(bbox):
    x1, y1, x2, y2 = bbox
    center_x = int((x1+x2) / 2)
    center_y = int((y1+y2) / 2)
    return center_x, center_y


def dist(pt1, pt2):
    return (((pt1[0]-pt2[0]) ** 2) + ((pt1[1] - pt2[1])**2)) ** 0.5