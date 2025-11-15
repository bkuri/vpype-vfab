"""vsketch integration example."""

import vsketch


class MySketch(vsketch.SketchClass):
    """Example sketch demonstrating vpype-plotty integration."""

    def draw(self, vsk: vsketch.Vsketch) -> None:
        """Draw the sketch."""
        vsk.size("a4", landscape=False)
        vsk.scale("cm")

        # Create generative pattern
        vsk.detail(0.01)  # High detail for plotting

        # Draw concentric circles
        for i in range(10):
            radius = 0.5 + i * 0.8
            vsk.circle(10, 15, radius)

        # Draw spiral pattern
        for angle in range(0, 720, 5):
            radius = angle / 100
            x = 10 + radius * vsk.cos(angle)
            y = 15 + radius * vsk.sin(angle)
            vsk.point(x, y)

        # Add some random elements
        for _ in range(20):
            x = vsk.random(5, 15)
            y = vsk.random(5, 25)
            size = vsk.random(0.2, 1.0)
            vsk.rect(x, y, size, size)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        """Finalize the sketch and add to vfab."""
        # Standard vpype optimization
        vsk.vpype("linemerge linesimplify reloop linesort")

        # Add to vfab with high-quality preset and auto-queue
        vsk.vpype("vfab-add --name vsketch_example --preset hq --queue")

        print("✓ Sketch added to vfab with high-quality preset")


if __name__ == "__main__":
    sketch = MySketch()
    sketch.display()
