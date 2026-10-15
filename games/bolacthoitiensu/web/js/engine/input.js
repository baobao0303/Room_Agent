/**
 * Input Module (web/js/engine/input.js)
 * Handles mouse, keyboard, touch events, screen-to-grid raycasting, and drag gestures.
 */

export class InputManager {
    constructor(canvas, camera) {
        this.canvas = canvas;
        this.camera = camera;

        // Keys currently pressed
        this.keys = new Set();

        // Mouse state
        this.mouse = {
            screenX: 0,
            screenY: 0,
            worldX: 0,
            worldY: 0,
            gridX: 0,
            gridY: 0,
            isDown: false,
            button: 0
        };

        // Dragging state for camera pan
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.dragDist = 0;

        // Grid dimensions
        this.TILE_WIDTH = 22;
        this.TILE_HEIGHT = 16;

        // Callbacks
        this.onTileClick = null;
        this.onEntityClick = null;
        this.onCancel = null;
        this.onKeyDown = null;

        this.setupListeners();
    }

    setupListeners() {
        // Mouse Move
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            // Scaling ratio in case canvas CSS size differs from internal width/height
            const scaleX = this.canvas.width / rect.width;
            const scaleY = this.canvas.height / rect.height;

            const clientX = (e.clientX - rect.left) * scaleX;
            const clientY = (e.clientY - rect.top) * scaleY;

            this.mouse.screenX = clientX;
            this.mouse.screenY = clientY;

            const world = this.camera.screenToWorld(clientX, clientY);
            this.mouse.worldX = world.x;
            this.mouse.worldY = world.y;

            // Grid coordinate mapping
            this.mouse.gridX = Math.floor(world.x / this.TILE_WIDTH);
            this.mouse.gridY = Math.floor(world.y / this.TILE_HEIGHT);

            if (this.isDragging) {
                const dx = e.clientX - this.dragStartX;
                const dy = e.clientY - this.dragStartY;
                this.dragDist += Math.hypot(dx, dy);

                // Invert delta to pan world opposite to mouse motion
                this.camera.moveBy(-dx, -dy);

                this.dragStartX = e.clientX;
                this.dragStartY = e.clientY;
            }
        });

        // Mouse Down
        this.canvas.addEventListener('mousedown', (e) => {
            this.mouse.isDown = true;
            this.mouse.button = e.button;

            if (e.button === 0 || e.button === 1 || e.button === 2) {
                this.isDragging = true;
                this.dragStartX = e.clientX;
                this.dragStartY = e.clientY;
                this.dragDist = 0;
            }
        });

        // Mouse Up
        window.addEventListener('mouseup', (e) => {
            if (this.mouse.isDown) {
                this.mouse.isDown = false;
                this.isDragging = false;

                // If movement was negligible, treat as a true click
                if (this.dragDist < 6 && (e.target === this.canvas || this.canvas.contains(e.target))) {
                    if (e.button === 0) {
                        if (this.onTileClick) {
                            this.onTileClick(this.mouse.gridX, this.mouse.gridY, this.mouse.worldX, this.mouse.worldY);
                        }
                    } else if (e.button === 2) {
                        // Right click cancels current placement or selection
                        if (this.onCancel) {
                            this.onCancel();
                        }
                    }
                }
            }
        });

        // Prevent context menu on right click
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());

        // Mouse Wheel (Zoom)
        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomDelta = e.deltaY < 0 ? 0.15 : -0.15;
            this.camera.zoomBy(zoomDelta);
        }, { passive: false });

        // Keyboard Down
        window.addEventListener('keydown', (e) => {
            this.keys.add(e.code);

            if (e.key === 'Escape') {
                if (this.onCancel) this.onCancel();
            }

            if (e.key === '+' || e.key === '=') {
                this.camera.zoomBy(0.2);
            } else if (e.key === '-' || e.key === '_') {
                this.camera.zoomBy(-0.2);
            }

            if (this.onKeyDown) {
                this.onKeyDown(e.key, e.code);
            }
        });

        // Keyboard Up
        window.addEventListener('keyup', (e) => {
            this.keys.delete(e.code);
        });

        // Touch support
        let touchStartDist = 0;
        this.canvas.addEventListener('touchstart', (e) => {
            if (e.touches.length === 1) {
                const t = e.touches[0];
                this.isDragging = true;
                this.dragStartX = t.clientX;
                this.dragStartY = t.clientY;
                this.dragDist = 0;
            } else if (e.touches.length === 2) {
                this.isDragging = false;
                touchStartDist = Math.hypot(
                    e.touches[0].clientX - e.touches[1].clientX,
                    e.touches[0].clientY - e.touches[1].clientY
                );
            }
        }, { passive: true });

        this.canvas.addEventListener('touchmove', (e) => {
            if (e.touches.length === 1 && this.isDragging) {
                const t = e.touches[0];
                const dx = t.clientX - this.dragStartX;
                const dy = t.clientY - this.dragStartY;
                this.dragDist += Math.hypot(dx, dy);

                this.camera.moveBy(-dx, -dy);
                this.dragStartX = t.clientX;
                this.dragStartY = t.clientY;
            } else if (e.touches.length === 2) {
                const dist = Math.hypot(
                    e.touches[0].clientX - e.touches[1].clientX,
                    e.touches[0].clientY - e.touches[1].clientY
                );
                const delta = (dist - touchStartDist) * 0.005;
                this.camera.zoomBy(delta);
                touchStartDist = dist;
            }
        }, { passive: true });

        this.canvas.addEventListener('touchend', (e) => {
            if (this.isDragging && this.dragDist < 10) {
                const rect = this.canvas.getBoundingClientRect();
                const scaleX = this.canvas.width / rect.width;
                const scaleY = this.canvas.height / rect.height;
                const clientX = (this.dragStartX - rect.left) * scaleX;
                const clientY = (this.dragStartY - rect.top) * scaleY;
                const world = this.camera.screenToWorld(clientX, clientY);
                const gx = Math.floor(world.x / this.TILE_WIDTH);
                const gy = Math.floor(world.y / this.TILE_HEIGHT);

                if (this.onTileClick) {
                    this.onTileClick(gx, gy, world.x, world.y);
                }
            }
            this.isDragging = false;
        });
    }

    /**
     * Continuous update called on game tick for WASD / Arrow camera panning
     */
    update() {
        let dx = 0;
        let dy = 0;
        const speed = 12;

        if (this.keys.has('KeyA') || this.keys.has('ArrowLeft')) dx -= speed;
        if (this.keys.has('KeyD') || this.keys.has('ArrowRight')) dx += speed;
        if (this.keys.has('KeyW') || this.keys.has('ArrowUp')) dy -= speed;
        if (this.keys.has('KeyS') || this.keys.has('ArrowDown')) dy += speed;

        if (dx !== 0 || dy !== 0) {
            this.camera.moveBy(dx, dy);
        }
    }
}
