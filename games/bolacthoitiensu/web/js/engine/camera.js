/**
 * Camera Module (web/js/engine/camera.js)
 * Provides smooth 2D world panning, edge-scrolling, zooming, and focus-target tracking.
 */

export class Camera {
    constructor(viewportWidth = 960, viewportHeight = 640) {
        this.viewportWidth = viewportWidth;
        this.viewportHeight = viewportHeight;

        // Current world camera position (top-left of viewport in world units)
        this.x = 0;
        this.y = 0;

        // Target position for smooth interpolation
        this.targetX = 0;
        this.targetY = 0;

        // Zoom scale
        this.zoom = 1.0;
        this.minZoom = 0.5;
        this.maxZoom = 2.5;

        // Map boundary limits
        this.mapWidthPx = 96 * 22;   // default 96 tiles * 22px
        this.mapHeightPx = 96 * 16;  // default 96 tiles * 16px

        // Panning speeds
        this.panSpeed = 16; // pixels per keyframe tick
        this.lerpSpeed = 0.15; // smooth damping factor
    }

    /**
     * Updates viewport dimensions on resize
     */
    setViewportSize(w, h) {
        this.viewportWidth = w;
        this.viewportHeight = h;
        this.clamp();
    }

    /**
     * Sets map boundaries to prevent camera from panning out of bounds
     */
    setMapBounds(tilesX, tilesY, tileW = 22, tileH = 16) {
        this.mapWidthPx = tilesX * tileW;
        this.mapHeightPx = tilesY * tileH;
        this.clamp();
    }

    /**
     * Instantly sets camera to focus on world coordinates (x, y)
     */
    centerOn(worldX, worldY) {
        const halfViewW = (this.viewportWidth / this.zoom) / 2;
        const halfViewH = (this.viewportHeight / this.zoom) / 2;

        this.x = worldX - halfViewW;
        this.y = worldY - halfViewH;
        this.targetX = this.x;
        this.targetY = this.y;
        this.clamp();
    }

    /**
     * Smoothly pans toward world coordinates (x, y)
     */
    focusOn(worldX, worldY) {
        const halfViewW = (this.viewportWidth / this.zoom) / 2;
        const halfViewH = (this.viewportHeight / this.zoom) / 2;

        this.targetX = worldX - halfViewW;
        this.targetY = worldY - halfViewH;
        this.clamp();
    }

    /**
     * Moves camera by delta (e.g. mouse drag or keyboard)
     */
    moveBy(deltaX, deltaY) {
        this.targetX += deltaX / this.zoom;
        this.targetY += deltaY / this.zoom;
        this.clamp();
    }

    /**
     * Changes zoom level around viewport center
     */
    setZoom(newZoom) {
        const clampedZoom = Math.max(this.minZoom, Math.min(this.maxZoom, newZoom));
        if (clampedZoom === this.zoom) return;

        // Keep center point stable during zoom
        const centerX = this.x + (this.viewportWidth / this.zoom) / 2;
        const centerY = this.y + (this.viewportHeight / this.zoom) / 2;

        this.zoom = clampedZoom;

        this.x = centerX - (this.viewportWidth / this.zoom) / 2;
        this.y = centerY - (this.viewportHeight / this.zoom) / 2;
        this.targetX = this.x;
        this.targetY = this.y;
        this.clamp();
    }

    zoomBy(delta) {
        this.setZoom(this.zoom + delta);
    }

    /**
     * Clamps position so camera doesn't wander beyond map edges
     */
    clamp() {
        const viewW = this.viewportWidth / this.zoom;
        const viewH = this.viewportHeight / this.zoom;

        const maxX = Math.max(0, this.mapWidthPx - viewW);
        const maxY = Math.max(0, this.mapHeightPx - viewH);

        this.targetX = Math.max(-100, Math.min(maxX + 100, this.targetX));
        this.targetY = Math.max(-100, Math.min(maxY + 100, this.targetY));

        this.x = Math.max(-100, Math.min(maxX + 100, this.x));
        this.y = Math.max(-100, Math.min(maxY + 100, this.y));
    }

    /**
     * Updates smooth lerp position per frame
     */
    update() {
        this.x += (this.targetX - this.x) * this.lerpSpeed;
        this.y += (this.targetY - this.y) * this.lerpSpeed;
        this.clamp();
    }

    /**
     * Transforms screen (canvas client) coordinates to world pixel coordinates
     */
    screenToWorld(screenX, screenY) {
        return {
            x: this.x + screenX / this.zoom,
            y: this.y + screenY / this.zoom
        };
    }

    /**
     * Transforms world pixel coordinates to screen (canvas client) coordinates
     */
    worldToScreen(worldX, worldY) {
        return {
            x: (worldX - this.x) * this.zoom,
            y: (worldY - this.y) * this.zoom
        };
    }
}
