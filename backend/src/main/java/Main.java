import spark.Request;
import spark.Response;

import static spark.Spark.get;

public class Main {
    public static void main(String[] args) {
        // 4567 is default port
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
