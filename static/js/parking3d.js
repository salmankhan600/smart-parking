/**
 * Park3D - Three.js Interactive 3D Parking Engine
 * Complete 3D Environment with procedural cars, slot raycasting, live polling, and smooth camera controls.
 */

class Park3DEngine {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;

        this.mallId = options.mallId || 1;
        this.floorId = options.floorId || 1;
        this.onSlotSelect = options.onSlotSelect || null;
        this.isAdmin = options.isAdmin || false;

        this.slotsData = [];
        this.slotMeshes = new Map(); // slotId -> THREE.Group / Mesh
        this.carMeshes = new Map();  // slotId -> THREE.Group (Procedural Car)

        this.selectedSlotId = null;
        this.hoveredSlotId = null;

        // Camera target lerp parameters
        this.isLerpingCamera = false;
        this.targetCameraPos = new THREE.Vector3();
        this.targetLookAt = new THREE.Vector3();

        this.activeFilter = 'all';

        this.initThree();
        this.createEnvironment();
        this.setupEventListeners();
        this.animate();

        // Load initial data and start 3-second polling
        this.loadFloorData();
        this.startPolling();
    }

    initThree() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        // 1. Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x050811);
        this.scene.fog = new THREE.FogExp2(0x050811, 0.008);

        // 2. Camera
        this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        this.camera.position.set(0, 35, 45);

        // 3. Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        this.container.appendChild(this.renderer.domElement);

        // 4. OrbitControls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI / 2 - 0.05; // Don't clip under floor
        this.controls.minDistance = 10;
        this.controls.maxDistance = 120;
        this.controls.target.set(0, 0, 0);

        // 5. Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
        this.scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0x00f3ff, 1.2);
        dirLight.position.set(30, 50, 30);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 0.5;
        dirLight.shadow.camera.far = 150;
        const d = 40;
        dirLight.shadow.camera.left = -d;
        dirLight.shadow.camera.right = d;
        dirLight.shadow.camera.top = d;
        dirLight.shadow.camera.bottom = -d;
        this.scene.add(dirLight);

        const secondaryLight = new THREE.DirectionalLight(0xff9900, 0.5);
        secondaryLight.position.set(-30, 30, -30);
        this.scene.add(secondaryLight);

        // Raycaster
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
    }

    createEnvironment() {
        // Floor Plane (Epoxy Concrete Grid)
        const floorGeo = new THREE.PlaneGeometry(80, 50);
        const floorMat = new THREE.MeshStandardMaterial({
            color: 0x0c1322,
            roughness: 0.4,
            metalness: 0.2
        });
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        this.scene.add(floor);

        // Grid lines overlay
        const grid = new THREE.GridHelper(80, 40, 0x00f3ff, 0x1e293b);
        grid.position.y = 0.01;
        this.scene.add(grid);

        // Central Road Lanes
        this.createRoadLanes();

        // Surrounding Concrete Walls & Pillars
        this.createPillarsAndWalls();

        // Entry & Exit Gate Arches
        this.createGates();
    }

    createRoadLanes() {
        const laneMat = new THREE.MeshBasicMaterial({ color: 0xffcc00 });
        
        // Horizontal driving lanes (yellow dashed lines)
        const laneGeo1 = new THREE.PlaneGeometry(60, 0.4);
        const lane1 = new THREE.Mesh(laneGeo1, laneMat);
        lane1.rotation.x = -Math.PI / 2;
        lane1.position.set(0, 0.02, -5);
        this.scene.add(lane1);

        const lane2 = new THREE.Mesh(laneGeo1, laneMat);
        lane2.rotation.x = -Math.PI / 2;
        lane2.position.set(0, 0.02, 5);
        this.scene.add(lane2);

        // Direction Arrows on Road (Procedural 3D arrow)
        this.createDirectionArrow(-20, -5);
        this.createDirectionArrow(0, -5);
        this.createDirectionArrow(20, -5);
    }

    createDirectionArrow(x, z) {
        const arrowGroup = new THREE.Group();
        const mat = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide });

        const stemGeo = new THREE.PlaneGeometry(0.6, 2.5);
        const stem = new THREE.Mesh(stemGeo, mat);
        stem.rotation.x = -Math.PI / 2;
        arrowGroup.add(stem);

        const headGeo = new THREE.ConeGeometry(0.8, 1.2, 3);
        const head = new THREE.Mesh(headGeo, mat);
        head.rotation.x = -Math.PI / 2;
        head.rotation.z = Math.PI;
        head.position.z = -1.5;
        arrowGroup.add(head);

        arrowGroup.position.set(x, 0.03, z);
        this.scene.add(arrowGroup);
    }

    createPillarsAndWalls() {
        const pillarMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 });
        const pillarGeo = new THREE.BoxGeometry(2, 8, 2);

        const positions = [
            [-35, -20], [0, -20], [35, -20],
            [-35, 20],  [0, 20],  [35, 20]
        ];

        positions.forEach(([x, z]) => {
            const pillar = new THREE.Mesh(pillarGeo, pillarMat);
            pillar.position.set(x, 4, z);
            pillar.castShadow = true;
            pillar.receiveShadow = true;
            this.scene.add(pillar);

            // Pillar hazard stripe top
            const topGeo = new THREE.BoxGeometry(2.1, 0.5, 2.1);
            const topMat = new THREE.MeshBasicMaterial({ color: 0xffb700 });
            const topBox = new THREE.Mesh(topGeo, topMat);
            topBox.position.set(x, 7.5, z);
            this.scene.add(topBox);
        });
    }

    createGates() {
        // Entry Gate Arch (Left)
        const entryGate = this.buildArch("ENTRY GATE", 0x00ff66);
        entryGate.position.set(-36, 0, 0);
        this.scene.add(entryGate);

        // Exit Gate Arch (Right)
        const exitGate = this.buildArch("EXIT GATE", 0xff3366);
        exitGate.position.set(36, 0, 0);
        this.scene.add(exitGate);
    }

    buildArch(labelText, neonColorHex) {
        const group = new THREE.Group();
        const frameMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.3 });

        const postGeo = new THREE.BoxGeometry(0.8, 6, 0.8);
        const post1 = new THREE.Mesh(postGeo, frameMat);
        post1.position.set(0, 3, -4);
        const post2 = new THREE.Mesh(postGeo, frameMat);
        post2.position.set(0, 3, 4);

        const beamGeo = new THREE.BoxGeometry(1, 0.8, 8.8);
        const beam = new THREE.Mesh(beamGeo, frameMat);
        beam.position.set(0, 6, 0);

        const signMat = new THREE.MeshBasicMaterial({ color: neonColorHex });
        const signGeo = new THREE.BoxGeometry(1.1, 0.6, 6);
        const sign = new THREE.Mesh(signGeo, signMat);
        sign.position.set(0, 6, 0);

        group.add(post1, post2, beam, sign);
        return group;
    }

    // Load Parking Data from Backend API
    async loadFloorData() {
        try {
            const res = await fetch(`/api/parking/${this.mallId}/${this.floorId}`);
            const data = await res.json();
            if (data.success) {
                this.slotsData = data.slots;
                this.renderSlots(data.slots);
                
                // Update metrics UI if present
                if (window.updateOccupancyMetrics) {
                    window.updateOccupancyMetrics(data.metrics);
                }
            }
        } catch (err) {
            console.error("Error fetching 3D parking slots:", err);
        }
    }

    startPolling() {
        if (this.pollingInterval) clearInterval(this.pollingInterval);
        this.pollingInterval = setInterval(() => {
            this.loadFloorData();
        }, 3000);
    }

    renderSlots(slots) {
        slots.forEach(slot => {
            const slotId = slot.id;
            
            // Check if slot mesh already exists
            let slotGroup = this.slotMeshes.get(slotId);

            if (!slotGroup) {
                slotGroup = this.createSlotMesh(slot);
                this.scene.add(slotGroup);
                this.slotMeshes.set(slotId, slotGroup);
            } else {
                // Update existing slot status color
                this.updateSlotStatusVisual(slotGroup, slot);
            }

            // Manage 3D Car inside Occupied slots
            if (slot.status === 'occupied') {
                if (!this.carMeshes.has(slotId)) {
                    const car = this.createProceduralCar(slot.vehicle_type);
                    car.position.set(slot.x_position, 0.5, slot.z_position);
                    this.scene.add(car);
                    this.carMeshes.set(slotId, car);
                }
            } else {
                if (this.carMeshes.has(slotId)) {
                    this.scene.remove(this.carMeshes.get(slotId));
                    this.carMeshes.delete(slotId);
                }
            }
        });
    }

    createSlotMesh(slot) {
        const group = new THREE.Group();
        group.position.set(slot.x_position, 0, slot.z_position);
        group.userData = { slotId: slot.id, slotData: slot };

        // 1. Slot Base Box Pad
        const padGeo = new THREE.BoxGeometry(4.2, 0.1, 7.5);
        const colorHex = this.getStatusColorHex(slot.status);
        
        const padMat = new THREE.MeshStandardMaterial({
            color: colorHex,
            roughness: 0.3,
            metalness: 0.5,
            emissive: colorHex,
            emissiveIntensity: 0.25
        });

        const pad = new THREE.Mesh(padGeo, padMat);
        pad.position.y = 0.05;
        pad.receiveShadow = true;
        pad.name = "slotPad";
        group.add(pad);

        // 2. White Parking Line Outlines
        const lineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
        const lineGeo = new THREE.BoxGeometry(0.15, 0.12, 7.5);
        
        const lineLeft = new THREE.Mesh(lineGeo, lineMat);
        lineLeft.position.set(-2.1, 0.06, 0);
        const lineRight = new THREE.Mesh(lineGeo, lineMat);
        lineRight.position.set(2.1, 0.06, 0);
        
        group.add(lineLeft, lineRight);

        // 3. EV Charger Prop (for EV Slots)
        if (slot.slot_type === 'ev') {
            const evCharger = this.createEVChargerProp();
            evCharger.position.set(0, 0, -3.2);
            group.add(evCharger);
        }

        // 4. Overhead LED Status Marker Light
        const ledGeo = new THREE.SphereGeometry(0.4, 16, 16);
        const ledMat = new THREE.MeshBasicMaterial({ color: colorHex });
        const led = new THREE.Mesh(ledGeo, ledMat);
        led.position.set(0, 4.5, -3.5);
        led.name = "ledLight";
        group.add(led);

        // LED light beam post
        const postGeo = new THREE.CylinderGeometry(0.05, 0.05, 4.5);
        const postMat = new THREE.MeshBasicMaterial({ color: 0x475569 });
        const post = new THREE.Mesh(postGeo, postMat);
        post.position.set(0, 2.25, -3.5);
        group.add(post);

        return group;
    }

    getStatusColorHex(status) {
        switch (status) {
            case 'available': return 0x00ff66; // Neon Green
            case 'reserved':  return 0xffb700; // Neon Yellow/Orange
            case 'occupied':  return 0xff3366; // Neon Red
            case 'disabled':  return 0x0088ff; // Neon Blue
            default:          return 0x94a3b8;
        }
    }

    updateSlotStatusVisual(group, slot) {
        group.userData.slotData = slot;
        const colorHex = this.getStatusColorHex(slot.status);

        const pad = group.getObjectByName("slotPad");
        if (pad) {
            pad.material.color.setHex(colorHex);
            pad.material.emissive.setHex(colorHex);
        }

        const led = group.getObjectByName("ledLight");
        if (led) {
            led.material.color.setHex(colorHex);
        }
    }

    // Procedural Low-Poly 3D Car Model Generator
    createProceduralCar(vehicleType = 'car') {
        const carGroup = new THREE.Group();

        let bodyWidth = 2.2, bodyLength = 4.2, bodyHeight = 1.0;
        let carColor = 0x38bdf8; // Sleek metallic cyan

        if (vehicleType === 'suv') {
            bodyWidth = 2.4; bodyLength = 4.6; bodyHeight = 1.3;
            carColor = 0xe2e8f0; // White SUV
        } else if (vehicleType === 'ev') {
            carColor = 0x10b981; // Emerald EV
        } else if (vehicleType === 'bike') {
            bodyWidth = 1.0; bodyLength = 2.2; bodyHeight = 1.0;
            carColor = 0xf59e0b; // Yellow Bike
        }

        // Main Car Body
        const bodyGeo = new THREE.BoxGeometry(bodyWidth, bodyHeight, bodyLength);
        const bodyMat = new THREE.MeshStandardMaterial({
            color: carColor,
            metalness: 0.8,
            roughness: 0.2
        });
        const body = new THREE.Mesh(bodyGeo, bodyMat);
        body.position.y = bodyHeight / 2 + 0.3;
        body.castShadow = true;
        carGroup.add(body);

        // Cabin / Roof (If not bike)
        if (vehicleType !== 'bike') {
            const cabinGeo = new THREE.BoxGeometry(bodyWidth * 0.85, bodyHeight * 0.8, bodyLength * 0.5);
            const cabinMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.1 });
            const cabin = new THREE.Mesh(cabinGeo, cabinMat);
            cabin.position.set(0, bodyHeight + 0.3, -0.2);
            cabin.castShadow = true;
            carGroup.add(cabin);

            // Headlights
            const lightGeo = new THREE.BoxGeometry(0.4, 0.2, 0.1);
            const lightMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
            const head1 = new THREE.Mesh(lightGeo, lightMat);
            head1.position.set(-0.7, bodyHeight / 2 + 0.3, bodyLength / 2 + 0.05);
            const head2 = new THREE.Mesh(lightGeo, lightMat);
            head2.position.set(0.7, bodyHeight / 2 + 0.3, bodyLength / 2 + 0.05);
            carGroup.add(head1, head2);
        }

        // 4 Wheels
        const wheelGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.3, 16);
        const wheelMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.9 });

        const wheelPositions = [
            [-bodyWidth / 2 - 0.1, 0.35,  bodyLength / 3],
            [ bodyWidth / 2 + 0.1, 0.35,  bodyLength / 3],
            [-bodyWidth / 2 - 0.1, 0.35, -bodyLength / 3],
            [ bodyWidth / 2 + 0.1, 0.35, -bodyLength / 3]
        ];

        wheelPositions.forEach(([x, y, z]) => {
            const wheel = new THREE.Mesh(wheelGeo, wheelMat);
            wheel.rotation.z = Math.PI / 2;
            wheel.position.set(x, y, z);
            wheel.castShadow = true;
            carGroup.add(wheel);
        });

        return carGroup;
    }

    createEVChargerProp() {
        const evGroup = new THREE.Group();
        const postMat = new THREE.MeshStandardMaterial({ color: 0x1e293b });
        const postGeo = new THREE.BoxGeometry(0.6, 1.8, 0.6);
        const post = new THREE.Mesh(postGeo, postMat);
        post.position.y = 0.9;

        const screenMat = new THREE.MeshBasicMaterial({ color: 0x00ff66 });
        const screenGeo = new THREE.BoxGeometry(0.4, 0.4, 0.05);
        const screen = new THREE.Mesh(screenGeo, screenMat);
        screen.position.set(0, 1.2, 0.31);

        evGroup.add(post, screen);
        return evGroup;
    }

    // Raycasting & User Interactions
    setupEventListeners() {
        window.addEventListener('resize', () => this.onWindowResize());
        this.renderer.domElement.addEventListener('pointermove', (e) => this.onPointerMove(e));
        this.renderer.domElement.addEventListener('pointerdown', (e) => this.onPointerDown(e));
    }

    onWindowResize() {
        if (!this.container) return;
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    getPointerPos(e) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    }

    onPointerMove(e) {
        this.getPointerPos(e);
        this.raycaster.setFromCamera(this.mouse, this.camera);

        const meshes = Array.from(this.slotMeshes.values());
        const intersects = this.raycaster.intersectObjects(meshes, true);

        if (intersects.length > 0) {
            let obj = intersects[0].object;
            while (obj.parent && !obj.userData.slotData) {
                obj = obj.parent;
            }
            if (obj.userData.slotData) {
                this.container.style.cursor = 'pointer';
                this.hoveredSlotId = obj.userData.slotData.id;
                return;
            }
        }
        this.container.style.cursor = 'default';
        this.hoveredSlotId = null;
    }

    onPointerDown(e) {
        this.getPointerPos(e);
        this.raycaster.setFromCamera(this.mouse, this.camera);

        const meshes = Array.from(this.slotMeshes.values());
        const intersects = this.raycaster.intersectObjects(meshes, true);

        if (intersects.length > 0) {
            let obj = intersects[0].object;
            while (obj.parent && !obj.userData.slotData) {
                obj = obj.parent;
            }
            if (obj.userData.slotData) {
                const slot = obj.userData.slotData;
                this.selectSlot(slot.id);
            }
        }
    }

    selectSlot(slotId) {
        this.selectedSlotId = slotId;
        const slotGroup = this.slotMeshes.get(slotId);
        if (!slotGroup) return;

        const slot = slotGroup.userData.slotData;

        // Animate camera focus to slot position
        this.focusCameraOn(slot.x_position, slot.z_position);

        // Execute callback
        if (this.onSlotSelect) {
            this.onSlotSelect(slot);
        }
    }

    focusCameraOn(x, z) {
        this.isLerpingCamera = true;
        this.targetLookAt.set(x, 0, z);
        this.targetCameraPos.set(x, 15, z + 18);
    }

    // Camera Presets
    setTopView() {
        this.isLerpingCamera = true;
        this.targetLookAt.set(0, 0, 0);
        this.targetCameraPos.set(0, 50, 0.1);
    }

    set3DView() {
        this.isLerpingCamera = true;
        this.targetLookAt.set(0, 0, 0);
        this.targetCameraPos.set(0, 35, 45);
    }

    // Filtering
    applyFilter(filterType) {
        this.activeFilter = filterType;
        this.slotMeshes.forEach((group, slotId) => {
            const slot = group.userData.slotData;
            let visible = true;

            if (filterType === 'ev' && slot.slot_type !== 'ev') visible = false;
            if (filterType === 'accessible' && slot.slot_type !== 'accessible') visible = false;
            if (filterType === 'available' && slot.status !== 'available') visible = false;

            group.visible = visible;
        });
    }

    // Animation Loop
    animate() {
        requestAnimationFrame(() => this.animate());

        // Handle camera smooth lerping
        if (this.isLerpingCamera) {
            this.camera.position.lerp(this.targetCameraPos, 0.08);
            this.controls.target.lerp(this.targetLookAt, 0.08);

            if (this.camera.position.distanceTo(this.targetCameraPos) < 0.2) {
                this.isLerpingCamera = false;
            }
        }

        // Hover scale bounce on LED lights
        this.slotMeshes.forEach((group, id) => {
            const led = group.getObjectByName("ledLight");
            if (led) {
                if (id === this.hoveredSlotId || id === this.selectedSlotId) {
                    led.scale.set(1.4, 1.4, 1.4);
                } else {
                    led.scale.set(1.0, 1.0, 1.0);
                }
            }
        });

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

window.Park3DEngine = Park3DEngine;
