import './globals.css';
import Link from 'next/link';
export const metadata={title:'FactoryVision OS',description:'Industrial visual inspection operations'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><header><Link className="brand" href="/">FACTORYVISION <b>OS</b></Link><nav><Link href="/operations">Operations</Link><Link href="/live">Live console</Link><Link href="/review">Review</Link><Link href="/mlops">MLOps</Link></nav><span className="status">● CONTROL PLANE ONLINE</span></header>{children}</body></html>}
