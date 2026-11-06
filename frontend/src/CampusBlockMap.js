import { Fragment as _Fragment, jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useMemo, useState } from 'react';
import { ArrowRight, ExternalLink, MapPinned, Navigation } from 'lucide-react';
import './campus-map.css';
const topRow = [38, 250, 462, 674];
const bottomRow = [38, 250, 462, 674];
const room = (id, label, index, row) => ({
    id, label, x: (row === 'top' ? topRow : bottomRow)[index], y: row === 'top' ? 56 : 286, width: 188, height: 82,
});
const rowBlocks = (labels, row) => labels.map((label, index) => room(label, label, index, row));
const floorPlans = [
    { building: 'IET', floor: 'Ground floor', blocks: [
            { id: 'library', label: 'Library', x: 38, y: 56, width: 400, height: 82 },
            { id: 'teachers-office', label: "Teachers' Office", x: 38, y: 286, width: 400, height: 82 },
            { id: 'placement-cell', label: 'Placement Cell', x: 462, y: 56, width: 400, height: 82 },
            { id: 'director-office', label: 'Director Office', x: 462, y: 286, width: 400, height: 82 },
            { id: 'entry-gate', label: 'Entry Gate', x: 365, y: 383, width: 170, height: 42 },
        ] },
    { building: 'IET', floor: 'First floor', blocks: [
            ...rowBlocks(['IET 22', 'IET 16', 'IET 14', 'IET 15'], 'top'),
            ...rowBlocks(['IET 20', 'IET 19', 'IET 18', 'IET 17'], 'bottom'),
        ] },
    { building: 'IET', floor: 'Second floor', blocks: [
            { id: 'IET 32', label: 'Seminar Hall · IET 32', x: 38, y: 56, width: 400, height: 82 },
            room('IET 24', 'IET 24', 2, 'top'),
            room('IET 25', 'IET 25', 3, 'top'),
            ...rowBlocks(['IET 30', 'IET 29', 'IET 28', 'IET 23'], 'bottom'),
        ] },
    { building: 'Deeksha Bhawan', floor: 'Ground floor', blocks: [
            ...rowBlocks(['LH01', 'LH02', 'LH03', 'LH04'], 'top'),
            ...rowBlocks(['LH05', 'LH06', 'LH07'], 'bottom'),
        ] },
    { building: 'Deeksha Bhawan', floor: 'First floor', blocks: [
            ...rowBlocks(['LH08', 'LH09', 'LH10', 'LH11'], 'top'),
            ...rowBlocks(['LH12', 'LH13', 'LH14'], 'bottom'),
        ] },
];
const buildingOptions = [...new Set(floorPlans.map(({ building }) => building))];
export default function CampusBlockMap() {
    const [building, setBuilding] = useState(buildingOptions[0]);
    const [floor, setFloor] = useState('Ground floor');
    const [startId, setStartId] = useState('');
    const [destinationId, setDestinationId] = useState('');
    const plan = floorPlans.find(item => item.building === building && item.floor === floor) ?? floorPlans[0];
    const availableFloors = floorPlans.filter(item => item.building === building);
    const start = plan.blocks.find(block => block.id === startId);
    const destination = plan.blocks.find(block => block.id === destinationId);
    const route = useMemo(() => {
        if (!start || !destination || start.id === destination.id)
            return null;
        const startX = start.x + start.width / 2;
        const destinationX = destination.x + destination.width / 2;
        const startOnTop = start.y < 180;
        const destinationOnTop = destination.y < 180;
        const startY = startOnTop ? start.y + start.height : start.y;
        const destinationY = destinationOnTop ? destination.y + destination.height : destination.y;
        if (startOnTop === destinationOnTop) {
            const corridorY = startOnTop ? 180 : 274;
            return `M ${startX} ${startY} L ${startX} ${corridorY} L ${destinationX} ${corridorY} L ${destinationX} ${destinationY}`;
        }
        const startLane = startOnTop ? 180 : 274;
        const destinationLane = destinationOnTop ? 180 : 274;
        return `M ${startX} ${startY} L ${startX} ${startLane} L 510 ${startLane} L 510 ${destinationLane} L ${destinationX} ${destinationLane} L ${destinationX} ${destinationY}`;
    }, [start, destination]);
    function changeBuilding(value) {
        const nextFloor = floorPlans.find(item => item.building === value)?.floor ?? 'Ground floor';
        setBuilding(value);
        setFloor(nextFloor);
        setStartId('');
        setDestinationId('');
    }
    function changeFloor(value) {
        setFloor(value);
        setStartId('');
        setDestinationId('');
    }
    return (_jsxs("section", { className: "campus-block-map", children: [_jsxs("header", { className: "campus-map-intro", children: [_jsxs("div", { children: [_jsxs("span", { className: "map-kicker", children: [_jsx(MapPinned, { size: 14 }), " BLOCK-TO-BLOCK WAYFINDING"] }), _jsx("h2", { children: "Choose a block. Find your way." }), _jsx("p", { children: "Pick a building, floor and two labeled blocks to display a route on the floor diagram." })] }), _jsx("div", { className: "map-orbit", children: _jsx(Navigation, { size: 27 }) })] }), _jsxs("div", { className: "block-map-layout", children: [_jsxs("section", { className: "panel block-map-panel", children: [_jsxs("div", { className: "block-map-controls", children: [_jsxs("label", { children: ["Building", _jsx("select", { value: building, onChange: event => changeBuilding(event.target.value), children: buildingOptions.map(option => _jsx("option", { children: option }, option)) })] }), _jsxs("label", { children: ["Floor", _jsx("select", { value: floor, onChange: event => changeFloor(event.target.value), children: availableFloors.map(item => _jsx("option", { children: item.floor }, item.floor)) })] }), _jsxs("label", { children: ["Start block", _jsxs("select", { value: startId, onChange: event => setStartId(event.target.value), children: [_jsx("option", { value: "", children: "Choose a starting block" }), plan.blocks.map(block => _jsx("option", { value: block.id, children: block.label }, block.id))] })] }), _jsxs("label", { children: ["Destination block", _jsxs("select", { value: destinationId, onChange: event => setDestinationId(event.target.value), children: [_jsx("option", { value: "", children: "Choose a destination" }), plan.blocks.map(block => _jsx("option", { value: block.id, children: block.label }, block.id))] })] })] }), _jsxs("div", { className: "block-map-heading", children: [_jsxs("div", { children: [_jsxs("h3", { children: [building, " \u00B7 ", floor] }), _jsx("p", { children: "Room labels transcribed from the supplied blueprint \u00B7 simplified block layout" })] }), _jsxs("span", { className: "block-map-legend", children: [_jsx("i", {}), " Route"] })] }), _jsx("div", { className: "block-map-canvas", children: _jsxs("svg", { viewBox: "0 0 900 450", role: "img", "aria-label": `${building} ${floor} block diagram`, children: [_jsx("rect", { className: "map-building-outline", x: "20", y: "35", width: "860", height: "350", rx: "14" }), _jsx("rect", { className: "map-corridor", x: "28", y: "174", width: "844", height: "98", rx: "12" }), _jsx("text", { className: "map-corridor-label", x: "52", y: "235", children: "MAIN CORRIDOR" }), _jsxs("g", { className: "map-stairs", children: [_jsx("rect", { x: "416", y: "188", width: "68", height: "70", rx: "8" }), _jsx("path", { d: "M428 246h44M428 238h44M428 230h44M428 222h44M428 214h44M428 206h44M428 198h44" }), _jsx("text", { x: "450", y: "273", textAnchor: "middle", children: "STAIRS" })] }), plan.blocks.map(block => {
                                            const isStart = block.id === startId;
                                            const isDestination = block.id === destinationId;
                                            return (_jsxs("g", { className: `map-room${isStart ? ' is-start' : ''}${isDestination ? ' is-destination' : ''}`, children: [_jsx("rect", { x: block.x, y: block.y, width: block.width, height: block.height, rx: "9" }), _jsx("text", { x: block.x + block.width / 2, y: block.y + block.height / 2, textAnchor: "middle", dominantBaseline: "middle", children: block.label.toUpperCase() }), isStart && _jsx("text", { className: "map-point-label", x: block.x + block.width / 2, y: block.y + block.height + 16, textAnchor: "middle", children: "START" }), isDestination && _jsx("text", { className: "map-point-label", x: block.x + block.width / 2, y: block.y - 9, textAnchor: "middle", children: "DESTINATION" })] }, block.id));
                                        }), route && _jsx("path", { className: "map-route-path", d: route, markerEnd: "url(#routeArrow)" }), _jsx("defs", { children: _jsx("marker", { id: "routeArrow", markerWidth: "8", markerHeight: "8", refX: "6", refY: "4", orient: "auto", children: _jsx("path", { d: "M0,0 L8,4 L0,8 z", className: "map-route-arrow" }) }) })] }) }), _jsx("div", { className: `block-route-status${route ? ' has-route' : ''}`, role: "status", "aria-live": "polite", children: route
                                    ? _jsxs(_Fragment, { children: [_jsx(Navigation, { size: 16 }), _jsxs("span", { children: [_jsx("b", { children: start?.label }), _jsx(ArrowRight, { size: 14 }), _jsx("b", { children: destination?.label })] })] })
                                    : _jsxs(_Fragment, { children: [_jsx(MapPinned, { size: 16 }), _jsx("span", { children: "Choose two different blocks on this floor to display the route." })] }) }), _jsx("p", { className: "block-map-disclaimer", children: "Illustrative block-to-block route based on the supplied blueprint, not GPS or a verified accessible route. Department names are not assigned to room blocks yet, and the simplified corridor layout may differ from the building; confirm locations and follow campus signage." })] }), _jsxs("section", { className: "panel real-map-panel", children: [_jsxs("div", { className: "real-map-heading", children: [_jsxs("div", { children: [_jsxs("span", { className: "map-kicker", children: [_jsx(MapPinned, { size: 13 }), " DDUGU CAMPUS MAP"] }), _jsx("h3", { children: "DDUGU campus" }), _jsx("p", { children: "Campus boundary view \u00B7 Gorakhpur, Uttar Pradesh" })] }), _jsx("a", { className: "real-map-open", href: "https://www.openstreetmap.org/?mlat=26.7540562&mlon=83.3845275#map=16/26.7540562/83.3845275", target: "_blank", rel: "noreferrer", "aria-label": "Open DDUGU campus on OpenStreetMap", children: _jsx(ExternalLink, { size: 15 }) })] }), _jsx("iframe", { className: "real-campus-map", title: "OpenStreetMap view of Deen Dayal Upadhyaya Gorakhpur University campus", src: "https://www.openstreetmap.org/export/embed.html?bbox=83.3800311%2C26.7446644%2C83.3881195%2C26.7562735&layer=mapnik&marker=26.7540562%2C83.3845275", loading: "lazy", referrerPolicy: "no-referrer" }), _jsxs("div", { className: "real-map-location", children: [_jsx(MapPinned, { size: 15 }), _jsxs("span", { children: [_jsx("b", { children: "DDUGU campus" }), _jsx("small", { children: "26.754056, 83.384528 \u00B7 campus marker; department coordinates are not verified" })] })] }), _jsxs("div", { className: "department-map-notice", children: [_jsx("b", { children: "Department and Dean\u2019s Office pins need verified locations" }), _jsx("p", { children: "This map is zoomed to the DDUGU campus only. The available blueprint identifies IET and Deeksha Bhawan blocks, but does not verify each department or the Dean\u2019s Office location. No guessed department pins are shown." }), _jsxs("a", { href: "https://ddugu.ac.in", target: "_blank", rel: "noreferrer", children: ["Check the official DDUGU website ", _jsx(ExternalLink, { size: 12 })] })] }), _jsxs("p", { className: "map-attribution", children: ["Map data \u00A9 ", _jsx("a", { href: "https://www.openstreetmap.org/copyright", target: "_blank", rel: "noreferrer", children: "OpenStreetMap contributors" })] })] })] })] }));
}
