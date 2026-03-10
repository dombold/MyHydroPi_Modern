import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import NavBar from "./components/layout/NavBar";
import PageWrapper from "./components/layout/PageWrapper";
import Dashboard from "./pages/Dashboard";
import Timers from "./pages/Timers";
import Graphs from "./pages/Graphs";
import Dosage from "./pages/Dosage";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        {/* Multi-layered radial gradient background — light theme */}
        <div
          className="fixed inset-0 pointer-events-none"
          style={{
            background:
              "radial-gradient(ellipse 70% 50% at 15% 0%, rgba(119,182,255,0.18) 0%, transparent 60%)," +
              "radial-gradient(ellipse 50% 40% at 85% 100%, rgba(3,60,115,0.09) 0%, transparent 55%)," +
              "radial-gradient(ellipse 100% 100% at 50% 50%, #f0f8ff 0%, #e8f4fd 100%)",
          }}
        />
        <NavBar />
        <main className="relative flex-1 z-10">
          <Routes>
            <Route path="/" element={<PageWrapper title="Dashboard"><Dashboard /></PageWrapper>} />
            <Route path="/timers" element={<PageWrapper title="Relay Timers"><Timers /></PageWrapper>} />
            <Route path="/graphs" element={<PageWrapper title="Sensor Graphs"><Graphs /></PageWrapper>} />
            <Route path="/dosage" element={<PageWrapper title="Dosage Calculator"><Dosage /></PageWrapper>} />
            <Route path="/settings" element={<PageWrapper title="Settings"><Settings /></PageWrapper>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
