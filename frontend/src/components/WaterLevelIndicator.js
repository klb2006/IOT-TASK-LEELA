import React from 'react';

const WaterLevelIndicator = ({ waterLiters, waterPercentage, loading = false }) => {
  const displayLiters = loading ? 'Loading...' : waterLiters.toFixed(1);
  const displayPercentage = loading ? '--' : waterPercentage.toFixed(1);

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      border: '1px solid #e0e0e0',
      padding: '24px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '20px',
      width: '100%',
      maxWidth: '300px'
    }}>
      {/* Header */}
      <h3 style={{
        color: '#999',
        fontSize: '12px',
        fontWeight: '600',
        letterSpacing: '1px',
        textTransform: 'uppercase',
        margin: 0
      }}>
        Water Volume
      </h3>

      {/* Tank Container */}
      <div style={{
        position: 'relative',
        width: '160px',
        height: '300px',
        backgroundColor: '#f0f4f8',
        border: '5px solid #60a5fa',
        borderRadius: '28px',
        overflow: 'hidden',
        boxShadow: '0 4px 12px rgba(0,0,0,0.12)'
      }}>
        {/* Water Fill */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: `${waterPercentage}%`,
          background: 'linear-gradient(to bottom, #60a5fa 0%, #3b82f6 50%, #1e40af 100%)',
          transition: 'height 5s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'flex-end',
          justifyContent: 'center',
          paddingBottom: '20px',
          boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.15)'
        }}>
          {/* Top Wave Layer - Gentle and Slow */}
          <svg
            style={{
              position: 'absolute',
              top: '-2px',
              left: 0,
              width: '100%',
              height: '32px',
              animation: 'wave1 16s ease-in-out infinite',
              opacity: 0.7
            }}
            viewBox="0 0 100 20"
            preserveAspectRatio="none"
          >
            <path
              d="M0,12 Q15,8 30,12 T60,12 T90,12 T120,12 L120,20 L0,20 Z"
              fill="rgba(255,255,255,0.4)"
            />
          </svg>

          {/* Bottom Wave Layer (opposite direction, slower) */}
          <svg
            style={{
              position: 'absolute',
              top: '2px',
              left: 0,
              width: '100%',
              height: '28px',
              animation: 'wave2 14s ease-in-out infinite reverse',
              opacity: 0.3
            }}
            viewBox="0 0 100 20"
            preserveAspectRatio="none"
          >
            <path
              d="M0,14 Q20,10 40,14 T80,14 T120,14 L120,20 L0,20 Z"
              fill="rgba(255,255,255,0.3)"
            />
          </svg>

          {/* Shimmer Effect - More Subtle */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '50px',
            background: 'linear-gradient(180deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 100%)',
            pointerEvents: 'none'
          }} />

          {/* Percentage Inside Water */}
          {waterPercentage > 10 && (
            <div style={{
              position: 'absolute',
              fontSize: '36px',
              fontWeight: '800',
              color: '#ffffff',
              textShadow: '0 3px 8px rgba(0,20,60,0.5), 0 0 10px rgba(0,0,0,0.3)',
              zIndex: 10,
              filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))'
            }}>
              {displayPercentage}%
            </div>
          )}
        </div>

        {/* Level Markings - Overlay */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '14px 10px',
          pointerEvents: 'none',
          zIndex: 5
        }}>
          {[100, 75, 50, 25, 0].map((mark) => (
            <div key={mark} style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <div style={{
                width: '10px',
                height: '1.5px',
                backgroundColor: waterPercentage >= mark ? 'rgba(255,255,255,0.5)' : '#999'
              }} />
              <span style={{
                fontSize: '11px',
                fontWeight: '600',
                color: waterPercentage >= mark ? 'rgba(255,255,255,0.7)' : '#aaa'
              }}>
                {mark}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Liters Display Below */}
      <div style={{
        textAlign: 'center'
      }}>
        <div style={{
          fontSize: '15px',
          color: '#555',
          fontWeight: '500'
        }}>
          {displayLiters}L
        </div>
      </div>

      <style>{`
        @keyframes wave1 {
          0% {
            transform: translateX(-50%);
          }
          50% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(50%);
          }
        }

        @keyframes wave2 {
          0% {
            transform: translateX(50%);
          }
          50% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50%);
          }
        }
      `}</style>
    </div>
  );
};

export default WaterLevelIndicator;
