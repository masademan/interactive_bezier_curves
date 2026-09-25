import numpy as np


def lerp(A: int | float | np.ndarray, B: int | float | np.ndarray, t: float) -> int | float | np.ndarray:
    """
    Lerp = Linear interpolation
    If 0 <= t <= 1, the output will be a lerp between A and B, where t = 0 gives A and t = 1 gives B
    If t < 0 or 1 < t, then it'll be exterpolating. Do be careful if you do that.
    """

    return (1 - t) * A + t * B


def nCr(n: int | float, r: int | float) -> int | float:
    """
    Calculates the combinatorical operation of nCr
    It's the equivalent of n! / (r! * (n - r)!), where n! is the factorial function
    However, this function doesn't use any recursion of other factorial function
    """

    if n == 0 or r == 0:
        return 1

    if r > n // 2:
        r = n - r

    output = 1

    for k in range(n - r + 1, n + 1):
        output *= k

    for k in range(2, r + 1):
        output /= k

    return output


def n_order_bezier(control_points: list[np.ndarray], t: float) -> np.ndarray:
    """
    Given the size of the control_points list, it'll make an n order bezier curve where n in the number of control points
    And t will be the lerp parameter to trace the curve.
    """
    t_prime = 1 - t
    n = len(control_points)

    control_point_shape = control_points[0].shape
    final_pos = np.zeros(control_point_shape)

    for k in range(n):
        if control_points[k].shape != control_point_shape:
            raise ValueError(f"Shape of control point {k + 1} is {control_points[k].shape}, not the expected shape {control_point_shape}")

        final_pos += nCr(n - 1, k) * t**k * t_prime ** (n - k - 1) * control_points[k]

    return final_pos


def get_bezier_curve_points(control_points: list[np.ndarray], resolution: int) -> list[np.ndarray]:
    """
    control_points is the list of control points to draw the Bezier curve. They have to all be the same dimensions
    resolution is the number of line segments to make the curve out of. Higher resolution means a smoother curve, but more computation. And the opposite is true if the resolution is lower.
    """
    sampled_bezier_curve_points = []
    
    for t in np.linspace(0, 1, num=resolution + 1):
        sampled_bezier_curve_points.append(n_order_bezier(control_points, t))
        
    return sampled_bezier_curve_points


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    resolution = 64
    
    control_points = [
        np.array([-2, 0]),
        np.array([-1.75, 2]),
        np.array([1.75, 2]),
        np.array([2, 0]),
    ]
    
    # Draw the control points
    matrix_control_points = np.array(control_points)
    plt.scatter(matrix_control_points[:, 0], matrix_control_points[:, 1], color="red", s=50, zorder=3)
    
    # Draw the sampled bezier curve points as well as the lines connecting them
    matrix_bezier_curve = np.array(get_bezier_curve_points(control_points, resolution))
    plt.plot(matrix_bezier_curve[:, 0], matrix_bezier_curve[:, 1], color="blue", linewidth="1.5", zorder=2)
    # plt.scatter(matrix_bezier_curve[1:-1, 0], matrix_bezier_curve[1:-1, 1], color="blue", s=10)

    # Set limits so the square is fully visible
    plt.xlim(-3, 3)
    plt.ylim(-3, 3)

    # Add grid and labels
    plt.gca().set_axisbelow(True)
    plt.grid(True)
    plt.xlabel("X Axis")
    plt.ylabel("Y Axis")
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title("Bezier curve test")

    # Show the plot
    plt.show()
