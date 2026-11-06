import { useMemo, useState } from 'react';
import { ArrowRight, ExternalLink, MapPinned, Navigation } from 'lucide-react';
import './campus-map.css';

type Block = { id: string; label: string; x: number; y: number; width: number; height: number };
type FloorPlan = { building: string; floor: string; blocks: Block[] };

const topRow = [38, 250, 462, 674];
const bottomRow = [38, 250, 462, 674];
const room = (id: string, label: string, index: number, row: 'top' | 'bottom'): Block => ({
  id, label, x: (row === 'top' ? topRow : bottomRow)[index], y: row === 'top' ? 56 : 286, width: 188, height: 82,
});
const rowBlocks = (labels: string[], row: 'top' | 'bottom') => labels.map((label, index) => room(label, label, index, row));

const floorPlans: FloorPlan[] = [
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
    if (!start || !destination || start.id === destination.id) return null;
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

  function changeBuilding(value: string) {
    const nextFloor = floorPlans.find(item => item.building === value)?.floor ?? 'Ground floor';
    setBuilding(value);
    setFloor(nextFloor);
    setStartId('');
    setDestinationId('');
  }

  function changeFloor(value: string) {
    setFloor(value);
    setStartId('');
    setDestinationId('');
  }

  return (
    <section className="campus-block-map">
      <header className="campus-map-intro">
        <div>
          <span className="map-kicker"><MapPinned size={14} /> BLOCK-TO-BLOCK WAYFINDING</span>
          <h2>Choose a block. Find your way.</h2>
          <p>Pick a building, floor and two labeled blocks to display a route on the floor diagram.</p>
        </div>
        <div className="map-orbit"><Navigation size={27} /></div>
      </header>

      <div className="block-map-layout">
        <section className="panel block-map-panel">
          <div className="block-map-controls">
            <label>Building
              <select value={building} onChange={event => changeBuilding(event.target.value)}>
                {buildingOptions.map(option => <option key={option}>{option}</option>)}
              </select>
            </label>
            <label>Floor
              <select value={floor} onChange={event => changeFloor(event.target.value)}>
                {availableFloors.map(item => <option key={item.floor}>{item.floor}</option>)}
              </select>
            </label>
            <label>Start block
              <select value={startId} onChange={event => setStartId(event.target.value)}>
                <option value="">Choose a starting block</option>
                {plan.blocks.map(block => <option key={block.id} value={block.id}>{block.label}</option>)}
              </select>
            </label>
            <label>Destination block
              <select value={destinationId} onChange={event => setDestinationId(event.target.value)}>
                <option value="">Choose a destination</option>
                {plan.blocks.map(block => <option key={block.id} value={block.id}>{block.label}</option>)}
              </select>
            </label>
          </div>

          <div className="block-map-heading">
            <div><h3>{building} · {floor}</h3><p>Room labels transcribed from the supplied blueprint · simplified block layout</p></div>
            <span className="block-map-legend"><i /> Route</span>
          </div>
          <div className="block-map-canvas">
            <svg viewBox="0 0 900 450" role="img" aria-label={`${building} ${floor} block diagram`}>
              <rect className="map-building-outline" x="20" y="35" width="860" height="350" rx="14" />
              <rect className="map-corridor" x="28" y="174" width="844" height="98" rx="12" />
              <text className="map-corridor-label" x="52" y="235">MAIN CORRIDOR</text>
              <g className="map-stairs">
                <rect x="416" y="188" width="68" height="70" rx="8" />
                <path d="M428 246h44M428 238h44M428 230h44M428 222h44M428 214h44M428 206h44M428 198h44" />
                <text x="450" y="273" textAnchor="middle">STAIRS</text>
              </g>
              {plan.blocks.map(block => {
                const isStart = block.id === startId;
                const isDestination = block.id === destinationId;
                return (
                  <g className={`map-room${isStart ? ' is-start' : ''}${isDestination ? ' is-destination' : ''}`} key={block.id}>
                    <rect x={block.x} y={block.y} width={block.width} height={block.height} rx="9" />
                    <text x={block.x + block.width / 2} y={block.y + block.height / 2} textAnchor="middle" dominantBaseline="middle">{block.label.toUpperCase()}</text>
                    {isStart && <text className="map-point-label" x={block.x + block.width / 2} y={block.y + block.height + 16} textAnchor="middle">START</text>}
                    {isDestination && <text className="map-point-label" x={block.x + block.width / 2} y={block.y - 9} textAnchor="middle">DESTINATION</text>}
                  </g>
                );
              })}
              {route && <path className="map-route-path" d={route} markerEnd="url(#routeArrow)" />}
              <defs><marker id="routeArrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" className="map-route-arrow" /></marker></defs>
            </svg>
          </div>
          <div className={`block-route-status${route ? ' has-route' : ''}`} role="status" aria-live="polite">
            {route
              ? <><Navigation size={16} /><span><b>{start?.label}</b><ArrowRight size={14} /><b>{destination?.label}</b></span></>
              : <><MapPinned size={16} /><span>Choose two different blocks on this floor to display the route.</span></>}
          </div>
          <p className="block-map-disclaimer">Illustrative block-to-block route based on the supplied blueprint, not GPS or a verified accessible route. Department names are not assigned to room blocks yet, and the simplified corridor layout may differ from the building; confirm locations and follow campus signage.</p>
        </section>
        <section className="panel real-map-panel">
          <div className="real-map-heading">
            <div>
              <span className="map-kicker"><MapPinned size={13} /> DDUGU CAMPUS MAP</span>
              <h3>DDUGU campus</h3>
              <p>Campus boundary view · Gorakhpur, Uttar Pradesh</p>
            </div>
            <a className="real-map-open" href="https://www.openstreetmap.org/?mlat=26.7540562&mlon=83.3845275#map=16/26.7540562/83.3845275" target="_blank" rel="noreferrer" aria-label="Open DDUGU campus on OpenStreetMap">
              <ExternalLink size={15} />
            </a>
          </div>
          <iframe
            className="real-campus-map"
            title="OpenStreetMap view of Deen Dayal Upadhyaya Gorakhpur University campus"
            src="https://www.openstreetmap.org/export/embed.html?bbox=83.3800311%2C26.7446644%2C83.3881195%2C26.7562735&layer=mapnik&marker=26.7540562%2C83.3845275"
            loading="lazy"
            referrerPolicy="no-referrer"
          />
          <div className="real-map-location">
            <MapPinned size={15} />
            <span><b>DDUGU campus</b><small>26.754056, 83.384528 · campus marker; department coordinates are not verified</small></span>
          </div>
          <div className="department-map-notice">
            <b>Department and Dean’s Office pins need verified locations</b>
            <p>This map is zoomed to the DDUGU campus only. The available blueprint identifies IET and Deeksha Bhawan blocks, but does not verify each department or the Dean’s Office location. No guessed department pins are shown.</p>
            <a href="https://ddugu.ac.in" target="_blank" rel="noreferrer">Check the official DDUGU website <ExternalLink size={12} /></a>
          </div>
          <p className="map-attribution">Map data © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap contributors</a></p>
        </section>
      </div>
    </section>
  );
}
