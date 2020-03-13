import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.ResultSet;

// assume that conn is an already created JDBC connection (see previous examples)

Statement stmt = null;
ResultSet results = null;

try {
    conn = DriverManager.getConnection("jdbc:mysql://localhost/test?user=minty&password=greatsqldb");

    stmt = conn.createStatement();
    results = stmt.executeQuery("SELECT foo FROM bar");

    //metadata contains information such as number of columns
    ResultSetMetaData rsmd = results.getMetaData();
    int numCols = rsmd.getColumnCount(), i;

    StringBuffer buf = new StringBuffer(); 

    while (results.next() && rowcount < 100)
    {
      for (i=1; i <= numCols; i++) 
      {
         if (i > 1) buf.append(",");
         buf.append(results.getString(i));
      }
      buf.append("\n");
    }
    
}
catch (SQLException ex){
    // handle any errors
    System.out.println("SQLException: " + ex.getMessage());
    System.out.println("SQLState: " + ex.getSQLState());
    System.out.println("VendorError: " + ex.getErrorCode());
}
finally {
    // it is a good idea to release
    // resources in a finally{} block
    // in reverse-order of their creation
    // if they are no-longer needed

    if (rs != null) {
        try {
            rs.close();
        } catch (SQLException sqlEx) { } // ignore

        rs = null;
    }

    if (stmt != null) {
        try {
            stmt.close();
        } catch (SQLException sqlEx) { } // ignore

        stmt = null;
    }

    if (con != null) {
        try {
            con.close();
        } catch (SQLException sqlEx) { } // ignore

        con = null;
    }
}