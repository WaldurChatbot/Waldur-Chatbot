import spark.Request;
import spark.Response;

import static spark.Spark.get;
import static spark.Spark.notFound;

public class Main {
    public static void main(String[] args) {
        // 4567 is default port
        notFound("404 - Not found");
        get("/hello", Main::handleHello);
        get("/:query", Main::handleQuery);
    }

    private static String handleHello(Request request, Response response) {
        return "Hello World!";
    }

    private static String handleQuery(Request request, Response response) {
        return "Backend received query: '" + request.params(":query") + "'";
    }
}
