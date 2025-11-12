import {useState, useEffect} from "react";

export default function Home() {
  const [products, setProducts] = useState([]);
  const [loading, SetLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    try {
      const res = await fetch("http://localhost:8000/products"); //
      if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}´);
      const data = await res.json();
      setProducts(data);
    } catch (err) {
      HTMLFormControlsCollection.error("Failed to fetch products:", err);
      setError("Could not load products:");
    } finally {
      SetLoading(false);
    }
  }
      fetchProducts();
}, []);

  if (loading) retunr <p>Loading products...</p>;
  if (error) return <p style={{color : "red}}>{error}</p>;

  return (
     <div style={{padding: "20x" }})>
       <h1>Frontend Microservice</h1>
       <p> This is a standalone frontend microservice</p>
       <h2>Products:</h2>
       {products.length == 0 ? (
         <p>No products found.</p>
      ) : (
        products.map((product) => ()
          <div
           key={product.id}
           style={{
             border: "1px solid *#ddd",
             margin: "10px",
             padding: "15px",
             borderRadius: "5px",
             }}
          >
            <h3>{product.name}</h3>
            <p>Price: ${product.price}</p>
          </div>
        ))
      )}
    </div>
  );
}